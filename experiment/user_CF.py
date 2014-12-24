#coding=utf8
import os,sys
import time
from collections import *
from models import BaseModel, BaseDataSet
import numpy as np
import logging
import json

class UserCF(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
		self.user_similarity = {}	# {uid:{sim_id:similarity}}
	
	def build_user_similarity(self,uids,user_sim_file):
		'''
		@Desc: building user similarity matrix
		@params[in] uids: {uid: [favor_songid,]}
		@params[in] user_sim_file: path to save user_similarity matrix
		@[output] user_similarity matrix to file
		'''
		time_st = time.time()

		songs_uid_mapping = defaultdict(list)	#{songid:[uid,]}
		for uid,songs in uids.iteritems():
			for song in songs:
				songs_uid_mapping[song].append(uid)
		
		uid_interSong = defaultdict(dict)
		for song, user_list in songs_uid_mapping.iteritems():
			for u in range(len(user_list)):
				for v in range(len(user_list)):
					if v == u:
						continue
					try:
						uid_interSong[user_list[u]][user_list[v]] += 1
					except:
						uid_interSong[user_list[u]][user_list[v]] = 1
		
		user_sim = defaultdict(dict)
		for uid,sim_users in uid_interSong.items():
			for vid,inter_num in sim_users.iteritems():
				user_sim[uid][vid] = inter_num / np.sqrt(len(uids[uid])*len(uids[vid]))
		self.user_similarity = user_sim
		
		#Dumping user_similarity matrix to file
		logging.info('Dumping user_similarity matrix to file:%s'%(user_sim_file))
		data_in_json = json.dumps(self.user_similarity)
		with open(user_sim_file,'wb') as fin:
			fin.write(data_in_json)
		logging.info('Dumping process done.')
	
		time_ed = time.time()
		self.cost_time = time_ed - time_st
	
	def load_user_similarity(self,user_sim_file):
		time_st = time.time()
		input_file = open(user_sim_file,'rb')
		self.user_similarity = json.loads(input_file.read())
		input_file.close()
		time_ed = time.time()
		self.cost_time = time_ed - time_st
		
	def recommend(self,uids,user_dict,song_dict,user_n=5,top_n=0):
		pass


def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	dataset = BaseDataSet()
	file_template = './dataset/user_dataset_%s_%s_%s'	#set_num,type,train_prob
	user_sim_file = './dataset/user_sim_%s_%s.json'%(set_level,train_prob)	# user-user simiarity matrix
	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test',train_prob)
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s"%(dataset.cost_time))
	print "DataForTrain: %s"%(train_file)
	print "DataForTest: %s"%(test_file)
	print "Dataset train_set info: %s"%(dataset.get_train_info())
	print "Dataset test_set info: %s"%(dataset.get_test_info())
	
	userCF_recommender = UserCF()
	if os.path.exists(user_sim_file):
		logging.info("File %s exists, loading user similarity matrix"%(user_sim_file))
		userCF_recommender.load_user_similarity(user_sim_file)
		logging.info("Build user_similarity cost: %s"%(userCF_recommender.cost_time))
	else:
		logging.info("File %s doesn't exist, building user similarity matrix"%(user_sim_file))
		userCF_recommender.build_user_similarity(dataset.train_data,user_sim_file)
		logging.info("Build user_similarity cost: %s"%(userCF_recommender.cost_time))

if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/userCf.log')
	logging.info("UserCF >>>>>>>>>>>> Start")
	main()
	logging.info("UserCF >>>>>>>>>>>> Complete")
	
