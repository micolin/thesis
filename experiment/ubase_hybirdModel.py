#coding=utf8
import os,sys
from collections import *
import logging,json,time
from models import BaseModel, BaseDataSet
from user_CF import UserCF
from user_tag_CF import UserTagCF
from userLDA import UserLDA

class HybirdModel_UB(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
		self.user_similarity = defaultdict(dict)
		self.userCF = UserCF()
		self.userTag = UserTagCF()
		self.userLda = UserLDA()

	def hybird_user_sim(self,user_songs, user_sim_file, hybird_sim_file, hybird_type='tag',theta=0.5):
		time_st = time.time()
		self.userCF.load_user_similarity(user_sim_file)
		if hybird_type == 'tag':
			self.userTag.load_user_similarity(hybird_sim_file)
		elif hybird_type == 'lda':
			self.userLda.load_user_similarity(hybird_sim_file)
		
		#Rebuild user_similarity matrix
		for uid in user_songs.keys():
			candidate_user = defaultdict(float)
			'''
			user_sim = user_tag_sim*theta*(1+user_lda_sim*(1-theta)) 
				greater than 
			user_sim= user_tag_sim * theta + user_lda_sim*(1-theta)
			'''
			for (vid,sim) in self.userCF.user_similarity[uid]:
				candidate_user[vid] += sim * theta + 1
			if hybird_type == 'tag':
				for (vid,sim) in self.userTag.user_similarity[uid]:
					candidate_user[vid] *= (1+sim*(1-theta))
			elif hybird_type == 'lda':
				for (vid,sim) in self.userLda.user_similarity[uid]:
					candidate_user[vid] *= (1+sim * (1-theta))

			#Sort sim user:
			sorted_sim_user = sorted(candidate_user.items(),key=lambda x:x[1],reverse=True)
			self.user_similarity[uid] = sorted_sim_user[:500]
		time_ed = time.time()
		logging.info('Rebuild user-similarity matrix cost:%s'%(time_ed-time_st))

	def recommend(self,user_songs,user_tags,item_tags,user_k,top_n,reorder=0):
		time_st = time.time()
		for uid in user_songs.keys():
			candidate_songs = defaultdict(float)
			top_k_users = self.user_similarity[uid][:user_k]
			for (vid,sim) in top_k_users:
				for song in set(user_songs[vid])-set(user_songs[uid]):
					candidate_songs[song] += sim
			if reorder:
				top_n_songs = sorted(candidate_songs.items(),key=lambda x:x[1], reverse=True)[:top_n*4]
				top_n_songs = self.reorder_withItemTag(user_tags[uid],item_tags,top_n_songs)[:top_n]
				self.result[uid] = [song[0] for song in top_n_songs]
			else:
				top_n_songs = sorted(candidate_songs.items(),key=lambda x:x[1], reverse=True)[:top_n]
				self.result[uid] = [song[0] for song in top_n_songs]
		time_ed = time.time()
		self.cost_time = time_ed - time_st

	def hybird_recommend_result(self,user_songs,user_k,top_n):
		time_st = time.time()
		for uid in user_songs.keys():
			candidate_songs = defaultdict(float)
			for (vid,sim) in self.userLda.user_similarity[uid][:user_k]:
				for song in set(user_songs[vid])-set(user_songs[uid]):
					candidate_songs[song]+= sim

			for (vid,sim) in self.userTag.user_similarity[uid][:user_k]:
				for song in set(user_songs[vid])-set(user_songs[uid]):
					candidate_songs[song] += sim
		
			top_n_songs = sorted(candidate_songs.items(),key=lambda x:x[1], reverse=True)[:top_n]
			self.result[uid] = [song[0] for song in top_n_songs]
		time_ed = time.time()
		self.cost_time = time_ed - time_st

	def hybird_result_withReorder(self,user_songs,user_tags,item_tags,user_k,top_n):
		time_st = time.time()
		for uid in user_songs.keys():
			candidate_songs = defaultdict(float)
			for (vid,sim) in self.userLda.user_similarity[uid][:user_k]:
				for song in set(user_songs[vid])-set(user_songs[uid]):
					candidate_songs[song]+= sim
			for (vid,sim) in self.userTag.user_similarity[uid][:user_k]:
				for song in set(user_songs[vid])-set(user_songs[uid]):
					candidate_songs[song]+= sim
		
			top_n_songs = sorted(candidate_songs.items(),key=lambda x:x[1], reverse=True)[:top_n*4]
			top_n_songs = self.reorder_withItemTag(user_tags[uid],item_tags,top_n_songs)[:top_n]
			self.result[uid] = [song[0] for song in top_n_songs]
		time_ed = time.time()
		self.cost_time = time_ed - time_st

	def reorder_withItemTag(self,user_tag_distrib,items_tag_distrib,top_n_songs):
		'''
		@Desc:
		@params[in] user_tag_distrib: dict, {tag:freq}
		@params[in] items_tag_distrib: dict, {sid:{tag:freq}}
		@params[in] top_n_songs: [(sid,score),]
		'''
		songs = set([song[0] for song in top_n_songs])
		user_norm = sum([freq**2 for freq in user_tag_distrib.values()])
		user_tags = set([tag for tag in user_tag_distrib.keys()])
		user_song_match = defaultdict(float)
		for sid in songs:
			inter_tag = user_tags & set(items_tag_distrib[sid].keys())
			song_norm = sum([freq**2 for freq in items_tag_distrib[sid].values()])
			if len(inter_tag) == 0:
				continue
			for tag in inter_tag:
				user_song_match[sid] += items_tag_distrib[sid][tag] * user_tag_distrib[tag]
			user_song_match[sid] /= (user_norm*song_norm)**0.5

		n_top_n_songs = sorted([(song[0],song[1]*(1+user_song_match[song[0]])) for song in top_n_songs],key=lambda x:x[1],reverse=True)
		return n_top_n_songs

def load_tag_distribution(object_tag_file):
	time_st = time.time()
	object_tag_dict = defaultdict(dict)
	with open(object_tag_file,'rb') as fin:
		for line in fin.readlines():
			line = line.strip().split('\t')
			sid = line[0]
			tags = json.loads(line[1])
			object_tag_dict[sid] = tags
	time_ed = time.time()
	logging.info("Load item-tag distribution cost:%s"%(time_ed-time_st))
	return object_tag_dict
			
def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	hybird_type = args[3]
	recommend_job = args[4]
	top_n = int(args[5])
	if hybird_type == 'lda':
		topic_num = int(args[6])
	
	#Log config
	log_file = './log/ubase_hybirdModel_%s_%s_%s_%s.log'%(set_level,train_prob,recommend_job,top_n)
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename=log_file,filemode='w')
	#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	
	#Filepath config
	file_template = './song_dataset/user_dataset_%s_%s_%s' #set_level, type, train_prob
	user_sim_file = './song_dataset/mid_data/user_sim_%s_%s.json'%(set_level,train_prob)
	if hybird_type == 'tag':
		userTag_sim_file = './song_dataset/mid_data/user_similarity_withTag_%s_%s.json'%(set_level,train_prob)
	if hybird_type == 'lda':
		userLDA_sim_file = './song_dataset/mid_data/user_sim_with_lda_%s_%s_%s.json'%(set_level,train_prob,topic_num)
	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test', train_prob)
	
	#Build dataset
	dataset = BaseDataSet()
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s"%(dataset.cost_time))
	print "DataForTrain: %s"%(train_file)
	print "DataForTest: %s"%(test_file)
	print "Dataset train_set info: %s"%(dataset.get_train_info())
	print "Dataset test_set info: %s"%(dataset.get_test_info())

	#Record best scores
	best_f_score = {'f_score':0}
	best_precision = {'precision':0}
	best_recall = {'recall':0}

	#Data Preparation
	items_tag_dict = {}
	users_tag_dict = {}
	if recommend_job in ('mix_result_reorder','mix_sim_reorder'):
		items_tag_dict = load_tag_distribution('./song_dataset/mid_data/song_tag_distribution.json')	#Load item_tag_distrib
		user_tag_file = './song_dataset/mid_data/user_tag_distribution_%s_%s.json'%(set_level,train_prob)
		users_tag_dict = load_tag_distribution(user_tag_file)

	#Initiate Hybird-Model
	recommender = HybirdModel_UB()
	if recommend_job in ('mix_sim','mix_sim_reorder'):
		if hybird_type == 'tag':
			recommender.hybird_user_sim(dataset.train_data,user_sim_file,userTag_sim_file,hybird_type='tag',theta=0.55)
		elif hybird_type == 'lda':
			recommender.hybird_user_sim(dataset.train_data,user_sim_file,userLDA_sim_file,hybird_type='lda',theta=0.55)
	elif recommend_job in ('mix_result','mix_result_reorder'):
		if hybird_type == 'tag':
			recommender.userTag.load_user_similarity(userTag_sim_file)
		elif hybird_type == 'lda':
			recommender.userLda.load_user_similarity(userLDA_sim_file)

	for user_k in range(20,101):
		if recommend_job == 'mix_sim':
			recommender.recommend(dataset.train_data,users_tag_dict,items_tag_dict,user_k,top_n,reorder=0)
		elif recommend_job == 'mix_sim_reorder':
			recommender.recommend(dataset.train_data,users_tag_dict,items_tag_dict,user_k,top_n,reorder=1)
		elif recommend_job == 'mix_result':
			recommender.hybird_recommend_result(dataset.train_data,user_k,top_n)
		elif recommend_job == 'mix_result_reorder':
			recommender.hybird_result_withReorder(dataset.train_data,users_tag_dict,items_tag_dict,user_k,top_n)
		logging.info("Train_prob:%s User_k:%s Top_n:%s cost:%s"%(train_prob,user_k,top_n,recommender.cost_time))
		scores = recommender.score(dataset.test_data)
		print "User_k:%s\tTop_n:%s\tScores:%s"%(user_k,top_n,scores)

		#Find Best Score
		if scores['f_score'] > best_f_score['f_score']:
			best_f_score = scores
			best_f_score['user_k'] = user_k
			best_f_score['top_n'] = top_n
		if scores['precision'] > best_precision['precision']:
			best_precision = scores
			best_precision['user_k']=user_k
			best_precision['top_n'] = top_n
		if scores['recall'] > best_recall['recall']:
			best_recall = scores
			best_recall['user_k']=user_k
			best_recall['top_n'] = top_n
	
	print "Best_F_Score: %s"%(best_f_score)
	print "Best_Precision: %s"%(best_precision)
	print "Best_Recall: %s"%(best_recall)

if __name__=="__main__":
	main()
