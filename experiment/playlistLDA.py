#coding=utf8
import os,sys
import logging
import time
import numpy as np
from models import BaseModel, BaseDataSet
from collections import *
from storage import *
import json
from gensim import corpora, models, similarities

class Playlist:
	def __init__(self,pid,songs,hot):
		self.pid = pid
		self.songs = songs
		self.hot = hot

class PlaylistDataset(BaseDataSet):
	def __init__(self):
		BaseDataSet.__init__(self)
		self.playlists = []
	
	def build_playlist_info(self):
		db = db_connection()
		time_st = time.time()
		for pid in self.all_songs:
			try:
				record = get_item_with_id(pid,db,'playlist_info')
				songs = record['songs'].split(',')
				hot = record['play_times']
				self.playlists.append(Playlist(pid,songs,hot))
			except:
				pass
		time_ed = time.time()
		logging.info('Get playlist info from db cost:%s'%(time_ed-time_st))

class PlaylistLDA(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
		self.dictionary = None
		self.model = None
		self.playlists = []
		self.playlist_similarity = defaultdict(list)
		self.pids = []	#All playlist id
	
	def build_model(self,model_file,pl_list,topic_num=60):
		'''
		@Desc: building lda-model using dataset
		'''
		if os.path.exists(model_file):
			self.load_model(model_file)
			return

		time_st = time.time()
		self.pids = [playlist.pid for playlist in pl_list]
		self.playlists = [playlist.songs for playlist in pl_list]
		
		logging.info("Build dictionary for songs")
		self.dictionary = corpora.Dictionary(self.playlists)
		logging.info("Build corpus for all playlist")
		corpus = [self.dictionary.doc2bow(playlist) for playlist in self.playlists]
		logging.info('Transfrom corpus using tfidf model')
		tfidf_model = models.TfidfModel(corpus)
		corpus_tfidf = tfidf_model[corpus]
		logging.info("Training lda model with corpus")
		self.model =  models.ldamodel.LdaModel(corpus_tfidf,num_topics=topic_num,id2word=self.dictionary)
		logging.info("Model training done...")

		time_ed = time.time()
		logging.info("Build lda-model and dump to: %s cost: %s"%(model_file,time_ed-time_st))
		
	def load_model(self,model_file):
		time_st = time.time()
		time_ed = time.time()
		logging.info("Load lda-model from: %s cost: %s"%(model_file,time_ed-time_st))
		
	def get_playlist_topics(self):
		'''
		@Desc: get topic-distribution from model for all playlist 
		'''
		pid_topics = defaultdict(dict)				#{pid:{topic:prob, }, }
		playlist_norm = defaultdict(float)			#{pid:norm^2 of vector}
		playlist_topics = defaultdict(set)			#{pid:set(topics)}
		for i in range(len(self.pids)):
			for (topic,prob) in self.model[self.dictionary.doc2bow(self.playlists[i])]:
				pid = self.pids[i]
				pid_topics[pid][topic]=prob
				playlist_norm[pid] += prob*prob
				playlist_topics[pid].add(topic)
		return pid_topics,playlist_norm,playlist_topics
	
	def build_playlist_similarity(self,playlist_sim_file,model_file,pl_list,topic_num=60,top_pl_k=500):
		if os.path.exists(playlist_sim_file):
			self.load_playlist_similarity(playlist_sim_file)
			return

		#Build lda-model if playlist_sim_file does not exist
		self.build_model(model_file,pl_list,topic_num)
		
		#Calculate similarity between each playlists
		time_st = time.time()
		pid_topics,playlist_norm,playlist_topics = self.get_playlist_topics()

		fin = open(playlist_sim_file,'wb')
		for idx,pid in enumerate(pid_topics.keys()):
			logging.info('Calculating similarity of sid:%s #%s'%(pid,idx))
			sim_playlist_dict = defaultdict(float)
			for vid in pid_topics.keys():
				if vid == pid:
					continue
				sum_prod = 0
				inter_topic = playlist_topics[pid] & playlist_topics[vid]
				for topic in inter_topic:
					sum_prod += pid_topics[pid][topic] * pid_topics[vid][topic]
				if sum_prod == 0:
					continue
				sim_playlist_dict[vid] = sum_prod / np.sqrt(playlist_norm[pid]*playlist_norm[vid])
		
			#Sorting sim_playlist_dict
			sorted_sim_playlist = sorted(sim_playlist_dict.items(),key=lambda x:x[1],reverse=True)[:top_pl_k]
			self.playlist_similarity[pid]=sorted_sim_playlist
			
			data_in_json = json.dumps(sorted_sim_playlist)
			fin.write("%s\t%s\n"%(pid,data_in_json))
		
		fin.close()	
		time_ed = time.time()
		logging.info("Calculate item-similarity cost: %s"%(time_ed-time_st))

	def load_playlist_similarity(self,playlist_sim_file):
		time_st = time.time()
		with open(playlist_sim_file,'rb') as fin:
			for line in fin.readlines():
				line = line.strip().split('\t')
				pid = line[0]
				sim_playlists = json.loads(line[1])
				self.playlist_similarity[pid] = sim_playlists
		
		time_ed = time.time()
		logging.info("Load item-similarity cost: %s"%(time_ed-time_st))

	def recommend(self,uids,item_k,top_n):
		time_st = time.time()
		for uid in uids.keys():
			candidate_playlists = defaultdict(float)
			remove_pid = set(uids[uid])
			for pid in uids[uid]:
				item_cnt = 0
				for (sim_pl,sim) in self.playlist_similarity[pid]:
					if item_cnt >= item_k:
						break
					if sim_pl in remove_pid:
						continue
					else:
						candidate_playlists[sim_pl] += sim
						item_cnt += 1
			top_n_playlists = sorted(candidate_playlists.items(),key=lambda x:x[1], reverse=True)[:top_n]
			self.result[uid] = [playlist[0] for playlist in top_n_playlists]
		
		time_ed = time.time()
		self.cost_time = time_ed - time_st
				
def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	topic_num = int(args[3])
	file_template = './pl_dataset/user_playlist_%s_%s_%s' #set_level,type,train_prob
	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test',train_prob)
	dataset=PlaylistDataset()
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s"%(dataset.cost_time))
	dataset.build_playlist_info()
	
	recommender = PlaylistLDA()
	playlist_sim_file = "./pl_dataset/mid_data/playlist_sim_with_lda_%s_%s_%s.json"%(set_level,train_prob,topic_num)
	model_file = "./pl_dataset/mid_data/lda_model_%s_%s_%s"%(set_level,train_prob,topic_num)
	recommender.build_playlist_similarity(playlist_sim_file,model_file,dataset.playlists,topic_num=topic_num,top_pl_k=500)
	
	print "DataForTrain: %s"%(train_file)
	print "DataForTest: %s"%(test_file)
	print "Dataset train_set info: %s"%(dataset.get_train_info())
	print "Dataset test_set info: %s"%(dataset.get_test_info())
	
	#Record best scores
	best_f_score = {'f_score':0}
	best_precision = {'precision':0}
	best_recall = {'recall':0}

	#Recommendation
	for item_k in range(10,80):
		for top_n in range(1,100,2):
			recommender.recommend(dataset.train_data,item_k=item_k,top_n=top_n)
			logging.info("Train_prob:%s Item_k:%s Top_n:%s Cost:%s"%(train_prob,item_k,top_n,recommender.cost_time))
			scores = recommender.score(dataset.test_data)
			print "Item_k:%s\tTop_n:%s\tScores:%s"%(item_k,top_n,scores)

			#Find Best Score
			if scores['f_score'] > best_f_score['f_score']:
				best_f_score = scores
				best_f_score['item_k'] = item_k
				best_f_score['top_n'] = top_n
			if scores['precision'] > best_precision['precision']:
				best_precision = scores
				best_precision['item_k']=item_k
				best_precision['top_n'] = top_n
			if scores['recall'] > best_recall['recall']:
				best_recall = scores
				best_recall['item_k']=item_k
				best_recall['top_n'] = top_n
			
	print "Best_F_Score: %s"%(best_f_score)
	print "Best_Precision: %s"%(best_precision)
	print "Best_Recall: %s"%(best_recall)

if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/playlistLDA.log',filemode='w')
	#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	main()
	
