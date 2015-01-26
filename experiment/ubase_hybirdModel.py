#coding=utf8
import os,sys
from collections import *
import logging,json,time
from models import BaseModel, BaseDataSet
from user_CF import UserCF
from user_tag_CF import UserTagCF
from userLDA import UserLDA

class HybirdModel_BU(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
		self.user_similarity = defaultdict(dict)
		self.userCF = UserCF()
		self.userTag = UserTagCF()
		self.userLda = UserLDA()

	def hybird_user_sim(self,user_songs, userTag_sim_file, userLDA_sim_file, theta=0.5):
		time_st = time.time()
		self.userTag.load_user_similarity(userTag_sim_file)
		self.userLda.load_user_similarity(userLDA_sim_file)
		
		#Rebuild user_similarity matrix
		for uid in user_songs.keys():
			candidate_user = defaultdict(float)
			#user_sim = user_tag_sim*theta*(1+user_lda_sim*(1-theta)) greater than user_sim= user_tag_sim * theta + user_lda_sim*(1-theta)
			for (vid,sim) in self.userTag.user_similarity[uid]:
				candidate_user[vid] += sim * theta
			for (vid,sim) in self.userLda.user_similarity[uid]:
				candidate_user[vid] *= (1+sim * (1-theta))

			#Sort sim user:
			sorted_sim_user = sorted(candidate_user.items(),key=lambda x:x[1],reverse=True)
			self.user_similarity[uid] = sorted_sim_user[:500]
		time_ed = time.time()
		logging.info('Rebuild user-similarity matrix cost:%s'%(time_ed-time_st))

	def recommend(self,user_songs,user_k,top_n):
		time_st = time.time()
		for uid in user_songs.keys():
			candidate_songs = defaultdict(float)
			top_k_users = self.user_similarity[uid][:user_k]
			for (vid,sim) in top_k_users:
				for song in set(user_songs[vid])-set(user_songs[uid]):
					candidate_songs[song] += sim
			top_n_songs = sorted(candidate_songs.items(),key=lambda x:x[1], reverse=True)[:top_n]
			self.result[uid] = [song[0] for song in top_n_songs]
		time_ed = time.time()
		self.cost_time = time_ed - time_st
		
	def hybird_recommend_result(self,user_songs, user_sim_file, userTag_sim_file, userLDA_sim_file,user_k,top_n):
		self.userCF.load_user_similarity(user_sim_file)
		self.userTag.load_user_similarity(userTag_sim_file)
		self.userLda.load_user_similarity(userLDA_sim_file)

		for uid in user_songs.keys():
			candidate_songs = defaultdict(float)
			for (vid,sim) in self.userCF.user_similarity[uid][:user_k]:
				for song in set(user_songs[vid])-set(user_songs[uid]):
					candidate_songs[song]+= sim

			for (vid,sim) in self.userTag.user_similarity[uid][:user_k]:
				for song in set(user_songs[vid])-set(user_songs[uid]):
					candidate_songs[song]+= sim *0
		
			top_n_songs = sorted(candidate_songs.items(),key=lambda x:x[1], reverse=True)[:top_n]
			self.result[uid] = [song[0] for song in top_n_songs]

def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	topic_num = int(args[3])
	top_n = int(args[4])
	recommend_job = args[5]
	
	#Filepath config
	file_template = './song_dataset/user_dataset_%s_%s_%s' #set_level, type, train_prob
	user_sim_file = './song_dataset/mid_data/user_sim_%s_%s.json'%(set_level,train_prob)
	userTag_sim_file = './song_dataset/mid_data/user_similarity_withTag_%s_%s.json'%(set_level,train_prob)
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

	#Build Hybird-Model
	recommender = HybirdModel()
	if recommend_job == 'mix_sim':
		recommender.hybird_user_sim(dataset.train_data,userTag_sim_file,userLDA_sim_file,theta=0.45)

	for user_k in range(20,101):
		if recommend_job == 'mix_sim':
			recommender.recommend(dataset.train_data,user_k,top_n)
		else:
			recommender.hybird_recommend_result(dataset.train_data,user_sim_file,userTag_sim_file,userLDA_sim_file,user_k,top_n)
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
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/hybirdModel.log',filemode='w')
	main()
