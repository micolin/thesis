#coding=utf8
import os,sys
import logging
import time
import numpy as np
from models import BaseModel, BaseDataSet
from collections import *
import json
try:
	from gensim import corpora, models, similarities
except:
	pass

class UserLDA(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
		self.dictionary = None
		self.model = None
		self.user_similarity = defaultdict(list)
	
	def build_model(self,uid_songs,topic_num=100):
		time_st = time.time()
		logging.info("Build dictionary for songs")
		self.dictionary = corpora.Dictionary(uid_songs.values())
		logging.info("Build corpus for all user")
		corpus = [self.dictionary.doc2bow(songs) for songs in uid_songs.values()]
		logging.info('Transfrom corpus using tfidf model')
		tfidf_model = models.TfidfModel(corpus)
		corpus_tfidf = tfidf_model[corpus]
		logging.info("Training lda model with corpus")
		self.model = models.ldamodel.LdaModel(corpus_tfidf,num_topics=topic_num,id2word=self.dictionary)
		logging.info("Model training done...")
		time_ed = time.time()
		logging.info("Build lda-model cost: %s"%(time_ed-time_st))

	def get_user_topicVector(self,uid_songs):
		uid_topics = defaultdict(dict)
		uid_norm = defaultdict(float)
		uid_topicSet = defaultdict(set)
		for uid,songs in uid_songs.items():
			for (topic,prob) in self.model[self.dictionary.doc2bow(songs)]:
				uid_topics[uid][topic]=prob
				uid_norm[uid] += prob*prob
				uid_topicSet[uid].add(topic)
		return uid_topics,uid_norm,uid_topicSet
	
	def build_user_similarity(self,user_sim_file,uid_songs,topic_num,top_user_k=500):
		if os.path.exists(user_sim_file):
			self.load_user_similarity(user_sim_file)
			return
		
		#Build user-lda model if user_sim_file does not exist
		self.build_model(uid_songs,topic_num)		
		
		#Calculate similarity between each users
		time_st = time.time()
		uid_topics, uid_norm, uid_topicSet = self.get_user_topicVector(uid_songs)	
		fin = open(user_sim_file,'wb')
		for idx,uid in enumerate(uid_songs.keys()):
			logging.info('Calculating similarity of uid:%s #%s'%(uid,idx))
			sim_user_dict = defaultdict(float)
			for vid in uid_songs.keys():
				if vid == uid:
					continue
				sum_prod = 0
				inter_topics = uid_topicSet[uid] & uid_topicSet[vid]
				for topic in inter_topics:
					sum_prod += uid_topics[uid][topic] * uid_topics[vid][topic]
				if sum_prod == 0:
					continue
				sim_user_dict[vid] = sum_prod / np.sqrt(uid_norm[uid]*uid_norm[vid])
			
			#Sorting sim_playlist_dict
			sorted_sim_user = sorted(sim_user_dict.items(),key=lambda x:x[1],reverse=True)[:top_user_k]
			self.user_similarity[uid]=sorted_sim_user
			
			#Dumping to file
			data_in_json = json.dumps(sorted_sim_user)
			fin.write('%s\t%s\n'%(uid,data_in_json))

		time_ed = time.time()
		logging.info("Calculate user-similarity cost: %s"%(time_ed-time_st))

	def load_user_similarity(self,user_sim_file,norm=0):
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

	def recommend(self,user_songs,user_k,top_n):
		time_st = time.time()
		for uid in user_songs.keys():
			candidate_songs = defaultdict(float)
			top_k_users = self.user_similarity[uid][:user_k]
			for (vid,sim) in top_k_users:
				for song in set(user_songs[vid])-set(user_songs[uid]):
					candidate_songs[song] += sim
			top_n_songs = sorted(candidate_songs.items(),key=lambda x:x[1], reverse=True)[:top_n]
			top_n_songs = [song[0] for song in top_n_songs]
			print "%s\t%s"%(uid,json.dumps(top_n_songs))	#输出top_n推荐结果到文件

		time_ed = time.time()
		self.cost_time = time_ed - time_st

def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	topic_num = int(args[3])
	user_k = int(args[4])
	try:
		top_n = int(args[5])
	except:
		top_n = 500
	
	#Log-Config
	logfile = './log/userLDA_%s_%s_%s.log'%(set_level,train_prob,topic_num)
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename=logfile)
	#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	
	#File path config
	user_sim_file = './song_dataset/mid_data/user_sim_with_lda_%s_%s_%s.json'%(set_level,train_prob,topic_num)
	file_template = './song_dataset/user_dataset_%s_%s_%s' #set_level, type, train_prob
	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test',train_prob)
	
	#Build dataset
	dataset = BaseDataSet()
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s"%(dataset.cost_time))
	
	#Initiate Recommender
	recommender = UserLDA()
	recommender.build_user_similarity(user_sim_file,dataset.train_data,topic_num=topic_num, top_user_k=300)
	
	#Recommendation
	recommender.recommend(dataset.train_data,user_k=user_k,top_n=top_n)
	logging.info("Train_prob:%s User_k:%s Top_n:%s cost:%s"%(train_prob,user_k,top_n,recommender.cost_time))

if __name__=="__main__":
	main()
