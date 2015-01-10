#coding=utf8
import os,sys
from collections import *
import logging,json,time
from models import BaseModel, BaseDataSet
from user_CF import UserCF
from userLDA import UserLDA

class HybirdModel(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
		self.user_similarity = defaultdict(dict)
		self.user_cf = UserCF()
		self.user_lda = UserLDA()

	def hybird_user_sim(self,user_songs, userCF_sim_file, userLDA_sim_file, theta=0.5):
		time_st = time.time()
		self.user_cf.load_user_similarity(userCF_sim_file)
		self.user_lda.load_user_similarity(userLDA_sim_file)
		
		#Rebuild user_similarity matrix
		for uid in user_songs.keys():
			candidate_user = defaultdict(float)
			for (vid,sim) in self.user_cf.user_similarity[uid]:
				candidate_user[vid] += sim * theta
			for (vid,sim) in self.user_lda.user_similarity[uid]:
				candidate_user[vid] += sim * (1-theta)

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
		
	def hybird_recommend_result(self,user_songs, userCF_sim_file, userLDA_sim_file,user_k,top_n):
		self.user_cf.load_user_similarity(userCF_sim_file)
		self.user_lda.load_user_similarity(userLDA_sim_file)
		
		self.user_cf.recommend(user_songs,user_k=user_k,top_n=top_n/2)
		self.user_lda.recommend(user_songs,user_k=user_k,top_n=top_n/2)
		
		for uid in user_songs.keys():
			self.result[uid] = self.user_cf.result[uid]+self.user_lda.result[uid]	
			print len(self.result[uid]),len(set(self.result[uid]))

def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	topic_num = int(args[3])
	top_n = int(args[4])
	
	file_template = './song_dataset/user_dataset_%s_%s_%s' #set_level, type, train_prob
	userCF_sim_file = './song_dataset/mid_data/user_sim_%s_%s.json'%(set_level,train_prob)
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
	recommender.hybird_recommend_result(dataset.train_data,userCF_sim_file,userLDA_sim_file,20,top_n)
	#recommender.hybird_user_sim(dataset.train_data,userCF_sim_file,userLDA_sim_file,theta=0.5)
	'''
	for user_k in range(20,100):
		recommender.recommend(dataset.train_data,user_k,top_n)
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
	'''
if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/hybirdModel.log',filemode='w')
	main()
