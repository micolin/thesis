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

		logging.info("Building user similarity...")
		#Build song-uid mapping
		logging.info('Building song-uid mapping')
		songs_uid_mapping = defaultdict(list)	#{songid:[uid,]}
		for uid,songs in uids.iteritems():
			for song in songs:
				songs_uid_mapping[song].append(uid)
		
		#Build interSong num matrix
		logging.info('Building interSong num matrix')
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
		
		logging.info("Calculating user-similarity")
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
		logging.info("Building user-similarity cost: %s"%(time_ed-time_st))
	
	def load_user_similarity(self,user_sim_file,norm=0):
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
				if norm and sim_users:
					max_sim = sim_users[0][1]
					sim_users = [[user[0],user[1]/max_sim] for user in sim_users]
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
			top_n_songs = [song[0] for song in top_n_songs]
			print "%s\t%s"%(uid,json.dumps(top_n_songs))	#输出top_n推荐结果到文件

		re_time_ed = time.time()
		self.cost_time = re_time_ed - re_time_st


def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	user_k = int(args[3])
	try:
		top_n = int(args[4])
	except:
		top_n = 500

	#File path config
	file_template = './song_dataset/user_dataset_%s_%s_%s'	#set_num,type,train_prob
	user_sim_file = './song_dataset/mid_data/user_sim_%s_%s.json'%(set_level,train_prob)	# user-user simiarity matrix
	
	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test',train_prob)

	#Build dataset
	dataset = BaseDataSet()
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s"%(dataset.cost_time))
	
	#Initiate Recommender
	recommender = UserCF()
	recommender.build_user_similarity(dataset.train_data,user_sim_file,top_user_k=1000)	#Top_user_k represent keep top k sim_user to file
	
	#Recommendation
	recommender.recommend(dataset.train_data,user_k=user_k,top_n=top_n)
	logging.info("Train_prob:%s User_k:%s Top_n:%s cost:%s"%(train_prob,user_k,top_n,recommender.cost_time))

if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/userCF.log')
	#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	main()
