#coding=utf8
import os,sys
import json,time
from collections import *
import logging
from models import BaseModel, BaseDataSet
from models import TopKHeap

class UserTagCF(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
		self.user_similarity = defaultdict(list)
		self.user_tag_distrib = defaultdict(dict)

	def load_item_tag(self,item_tag_file):
		'''
		@Desc: load item-tag distribtion from file
		@params[in] item_tag_file: path of file contains item-tag distribution
		'''
		time_st = time.time()
		song_tag_distrib = defaultdict(dict)
		with open(item_tag_file,'rb') as fin:
			for line in fin.readlines():
				line = line.strip().split('\t')
				sid = line[0]
				tag_dist = json.loads(line[1])
				song_tag_distrib[sid]=tag_dist
		time_ed = time.time()
		logging.info('Load item-tag distribution cost:%s'%(time_ed - time_st))
		return song_tag_distrib
	
	def build_userTagDistribution(self,user_songs,item_tag_file,user_tag_file):
		'''
		@Desc: build user-tag distribution from input_file
		@params[in]: user_songs: dict, {uid:[sid,]}
		@params[in]: item_tag_file: path of file contains item_tag distribution
		@params[in]: user_tag_file: path of output
		'''
		#Load user_tag distribution if user_tag_file exists
		if os.path.exists(user_tag_file):
			self.load_userTagDistribuition(user_tag_file)
			return
		
		#Load song_tag info from file
		song_tag_distrib = self.load_item_tag(item_tag_file)

		fin = open(user_tag_file,'wb')
		time_st = time.time()
		#Build user-tag distribution
		for uid,songs in user_songs.items():
			tag_dict = defaultdict(float)
			for song in songs:
				try:
					tag_freq_sum=sum(song_tag_distrib[song].values())	#Modify [accepted]
					for tag in song_tag_distrib[song].keys():
						#tag_dict[tag]+=1
						tag_dict[tag] += float(song_tag_distrib[song][tag])/tag_freq_sum	#Modify [accepted]
				except:
					#There's no tag info to the song
					pass
			self.user_tag_distrib[uid]=tag_dict
			
			#Dump to file
			data_in_json = json.dumps(tag_dict)
			fin.write('%s\t%s\n'%(uid,data_in_json))
		
		fin.close()
		time_ed = time.time()
		logging.info("Build user-tag distribution cost: %s"%(time_ed-time_st))

	def build_userTagDistribution_norm(self,user_songs,item_tag_file,user_tag_file):
		'''
		@Desc: build user-tag distribution from input_file
		@params[in]: user_songs: dict, {uid:[sid,]}
		@params[in]: item_tag_file: path of file contains item_tag distribution
		@params[in]: user_tag_file: path of output
		'''
		#Load user_tag distribution if user_tag_file exists
		if os.path.exists(user_tag_file):
			self.load_userTagDistribuition(user_tag_file)
			return
		
		#Load song_tag info from file
		song_tag_distrib = self.load_item_tag(item_tag_file)
		
		#Build user-tag distribution
		time_st = time.time()
		fin = open(user_tag_file,'wb')
		for uid,songs in user_songs.items():
			tag_dict = defaultdict(float)
			for song in songs:
				try:
					for tag in song_tag_distrib[song].keys():
						tag_dict[tag] += song_tag_distrib[song][tag]
				except:
					pass
			self.user_tag_distrib[uid]=tag_dict
			
			#Dump to file
			data_in_json = json.dumps(tag_dict)
			fin.write('%s\t%s\n'%(uid,data_in_json))
		
		fin.close()
		time_ed = time.time()
		logging.info("Build user-tag distribution cost: %s"%(time_ed-time_st))

	def load_userTagDistribuition(self,user_tag_file):
		time_st = time.time()
		with open(user_tag_file,'rb') as fin:
			for line in fin.readlines():
				line = line.strip().split('\t')
				uid = line[0]
				self.user_tag_distrib[uid] = json.loads(line[1])
		time_ed = time.time()
		logging.info("Load user-tag distribution cost: %s"%(time_ed-time_st))
	
	def normalize_tag_distrib(self):
		for uid, tags in self.user_tag_distrib.items():
			all_sum = sum(tags.values())
			for tag,freq in tags.items():
				self.user_tag_distrib[uid][tag]=float(freq)/all_sum

	def build_user_similarity(self,user_songs,user_sim_file,top_user_k=500):
		#Load user-similarity matrix from file if user_sim_file exists
		if os.path.exists(user_sim_file):
			self.load_user_similarity(user_sim_file)
			return

		#Build user-similarity for each user
		time_st = time.time()

		#Calculate normalization of each user
		user_norm = defaultdict(float)
		for uid in user_songs.keys():
			try:
				for tag,num in self.user_tag_distrib[uid].items():
					user_norm[uid] += num**2
			except:
				user_norm[uid] = 1

		#Calculate sim_users for each user
		fin = open(user_sim_file,'wb')
		for idx,uid in enumerate(user_songs.keys()):
			logging.info('Calculating similarity of uid:%s #%s'%(uid,idx))
			sim_user_dict = TopKHeap(top_user_k)
			for vid in user_songs.keys():
				if vid == uid:
					continue
				sum_prod = 0
				inter_tag = set(self.user_tag_distrib[uid].keys()) & set(self.user_tag_distrib[vid].keys())
				if len(inter_tag) == 0:
					continue
				for tag in inter_tag:
					sum_prod += self.user_tag_distrib[uid][tag] * self.user_tag_distrib[vid][tag]
				sim = sum_prod / (user_norm[uid]*user_norm[vid])**0.5
				sim_user_dict.push((vid,sim))
			self.user_similarity[uid] = sim_user_dict.topk()

			#Dump to file
			data_in_json = json.dumps(self.user_similarity[uid])
			fin.write("%s\t%s\n"%(uid,data_in_json))

		fin.close()
		time_ed = time.time()
		logging.info("Build user_similarity cost: %s"%(time_ed-time_st))

	def load_user_similarity(self,user_sim_file,norm=1):
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
		logging.info("Load user_similarity cost: %s"%(time_ed-time_st))

	def recommend(self,user_songs,user_k=20,top_n=50):
		'''
		@Desc: main process of recommendation
		@params[in] user_songs: {uid:[favor_songid,]}
		@params[in] user_k: use top_k similar user to recommend
		@params[in] top_n: recommend top_n songs to user
		'''
		re_time_st = time.time()
		for uid in user_songs.keys():
			top_n_users = self.user_similarity[uid][:user_k]
			candidate_songs = defaultdict(float)
			for (vid,sim) in top_n_users:
				for song in set(user_songs[vid])-set(user_songs[uid]):
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
		top_n = 500		#输出top500的推荐到文件
	
	#Filepath config
	item_tag_file = './song_dataset/mid_data/song_tag_distribution.json'
	user_tag_file = './song_dataset/mid_data/user_tag_distribution_%s_%s.json'%(set_level,train_prob)
	file_template = './song_dataset/user_dataset_%s_%s_%s'	#set_num,type,train_prob
	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test',train_prob)
	user_sim_file = './song_dataset/mid_data/user_similarity_withTag_%s_%s.json'%(set_level,train_prob)	
	
	#Build dataset
	dataset = BaseDataSet()
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s"%(dataset.cost_time))
	
	#Initiate recommender
	recommender = UserTagCF()
	recommender.build_userTagDistribution(dataset.train_data,item_tag_file,user_tag_file)
	recommender.build_user_similarity(dataset.train_data,user_sim_file,top_user_k=1000)		#保留用户的top1000个最相近的用户
	
	#Recommendation
	recommender.recommend(dataset.train_data,user_k=user_k,top_n=top_n)
	logging.info("Train_prob:%s User_k:%s Top_n:%s cost:%s"%(train_prob,user_k,top_n,recommender.cost_time))
	
if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/userTagCF.log',filemode='w')
	#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	main()
