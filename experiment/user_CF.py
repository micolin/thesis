#coding=utf8
import os,sys
import time
from collections import *
import numpy as np
from models import BaseModel, BaseDataSet
import logging
import json

class UserCF(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
		self.user_similarity = defaultdict(list)	# {uid:{sim_id:similarity}}
	
	def build_user_similarity(self,uids,user_sim_file,top_user_k=500):
		'''
		@Desc: building user similarity matrix
		@params[in] uids: {uid: [favor_songid,]}
		@params[in] user_sim_file: path to save user_similarity matrix
		@params[in] top_user_k: int, number of sim_user to be kept in user_similarity matrix
		@[out] user_similarity matrix to file
		'''
		#Load user-similarity matrix if user_sim_file exists
		if os.path.exists(user_sim_file):
			self.load_user_similarity(user_sim_file)
			return
		
		#Build user-similarity matrix
		time_st = time.time()

		#Build song-uid mapping
		songs_uid_mapping = defaultdict(list)	#{songid:[uid,]}
		for uid,songs in uids.iteritems():
			for song in songs:
				songs_uid_mapping[song].append(uid)
		
		#Build intetSong num matrix
		uid_interSong = defaultdict(dict)		#{uid:{uid:inter_num}}
		for song, user_list in songs_uid_mapping.iteritems():
			for u in range(len(user_list)):
				for v in range(len(user_list)):
					if v == u:
						continue
					try:
						uid_interSong[user_list[u]][user_list[v]] += 1
					except:
						uid_interSong[user_list[u]][user_list[v]] = 1
		
		fin = open(user_sim_file,'wb')
		for uid,sim_users in uid_interSong.items():
			sim_user_dict = defaultdict(float)
			for vid,inter_num in sim_users.iteritems():
				sim_user_dict[vid] = inter_num / np.sqrt(len(uids[uid])*len(uids[vid]))
			#Sorting sim_user_dict
			sorted_sim_user = sorted(sim_user_dict.items(), key=lambda x:x[1],reverse=True)[:top_user_k]
			self.user_similarity[uid] = sorted_sim_user

			#Dumping to file
			data_in_json = json.dumps(sorted_sim_user)
			fin.write('%s\t%s\n'%(uid,data_in_json))	
		
		time_ed = time.time()
		logging.info("Calculate user-similarity cost: %s"%(time_ed-time_st))
	
	def load_user_similarity(self,user_sim_file):
		'''
		@Desc: load user similarity matrix from file
		@params[in] user_sim_file: file of user_similarity json 
		'''
		time_st = time.time()
		with open(user_sim_file,'rb') as fin:
			for line in fin.readlines():
				line = line.strip().split('\t')
				uid = line[0]
				sim_users = json.loads(line[1])
				self.user_similarity[uid] = sim_users
		time_ed = time.time()
		logging.info("Load user-similarity cost: %s"%(time_ed-time_st))
		
	def recommend(self,uids,user_k=5,top_n=10):
		'''
		@Desc: main process of recommendation
		@params[in] uids: {uid:[favor_songid,]}
		@params[in] user_k: use top_k similar user to recommend
		@params[in] top_n: recommend top_n songs to user
		'''
		re_time_st = time.time()
		for uid in uids.keys():
			top_n_users = self.user_similarity[uid][:user_k]
			candidate_songs = defaultdict(float)
			for (vid,sim) in top_n_users:
				for song in set(uids[vid])-set(uids[uid]):
					candidate_songs[song]+=sim
			top_n_songs = sorted(candidate_songs.items(),key=lambda x:x[1],reverse=True)[:top_n]
			self.result[uid] = [song[0] for song in top_n_songs]

		re_time_ed = time.time()
		self.cost_time = re_time_ed - re_time_st


def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	e_type = args[3]	#Experiment type: song or playlist

	#File path config
	file_template = './song_dataset/user_dataset_%s_%s_%s'	#set_num,type,train_prob
	user_sim_file = './song_dataset/mid_data/user_sim_%s_%s.json'%(set_level,train_prob)	# user-user simiarity matrix
	if e_type == 'playlist':
		file_template = './pl_dataset/user_playlist_%s_%s_%s'	#set_num,type,train_prob
		user_sim_file = './pl_dataset/mid_data/user_sim_%s_%s.json'%(set_level,train_prob)	# user-user simiarity matrix
	
	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test',train_prob)

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

	#Initiate Recommender
	userCF_recommender = UserCF()
	userCF_recommender.build_user_similarity(dataset.train_data,user_sim_file,top_user_k=500)	#Top_user_k represent keep top k sim_user to file
	
	#Recommendation
	for user_k in range(40,80):
		for top_n in range(1,101,2):
			userCF_recommender.recommend(dataset.train_data,user_k=user_k,top_n=top_n)
			logging.info("Train_prob:%s User_k:%s Top_n:%s cost:%s"%(train_prob,user_k,top_n,userCF_recommender.cost_time))
			scores = userCF_recommender.score(dataset.test_data)
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
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/userCF.log',filemode='w')
	#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	main()
	
