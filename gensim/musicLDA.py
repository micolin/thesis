#coding=utf8
import os,sys
import logging
import time
import numpy as np
from collections import *
import json
from gensim import corpora, models, similarities

class Playlist:
	def __init__(self,pid,songs,tags,hot):
		self.pid = pid
		self.songlist = songs
		self.hot = hot
		self.tag = tags

class Dataset:
	def __init__(self):
		self.playlists = []
		self.cost_time = 0

	def build_dataset(self,input_path,hot_theta):
		time_st = time.time()
		with open(input_path,'rb') as fin:
			for line in fin.readlines():
				line = line.split('\t')
				pid = line[0]
				tags = line[6]
				hot = int(line[8])
				songs = line[11].split(',')
				if hot > hot_theta:
					playlist = Playlist(pid,songs,tags,hot)
					self.playlists.append(playlist)

		time_ed = time.time()
		self.cost_time = time_ed - time_st

class PlaylistLDA:
	def __init__(self):
		self.model = None
		self.playlists = []
		self.playlist_similarity = defaultdict(list)
		self.pids = []
		self.cost_time = 0
		self.dictionary = None

	def build_model(self,dataset):
		time_st = time.time()
		self.pids = [playlist.pid for playlist in dataset.playlists]
		self.playlists = [playlist.songlist for playlist in dataset.playlists]
		
		'''	
		#Find songs appear once
		song_cnt = defaultdict(int)
		for songs in self.playlists:
			for song in songs:
				song_cnt[song]+=1
		
		once_songs = set()
		for song, cnt in song_cnt.items():
			if cnt == 1:
				once_songs.add(song)
		'''

		logging.info('Build dictionary for songs')
		song_dictionary = corpora.Dictionary(self.playlists)
		self.dictionary = song_dictionary
		corpus = [song_dictionary.doc2bow(playlist) for playlist in self.playlists]
		logging.info('Transform corpus using tfidf model')
		tfidf = models.TfidfModel(corpus)
		corpus_tfidf = tfidf[corpus]
		logging.info("Training lda model with corpus")
		self.model = models.ldamodel.LdaModel(corpus_tfidf,num_topics=40,id2word=song_dictionary)
		logging.info("Model training done..")
		time_ed = time.time()
		self.cost_time = time_ed - time_st

	def get_playlist_topics(self):
		pid_topics = defaultdict(dict)
		for i in range(len(self.pids)):
			for (topic,prob) in self.model[self.dictionary.doc2bow(self.playlists[i])]:
				pid_topics[self.pids[i]][topic]=prob
		return pid_topics
	
	def build_playlist_similarity(self,playlist_sim_file,top_pl_k=500):
		time_st = time.time()
		pid_topics = self.get_playlist_topics()		#{pid:{topic:prob, }, }
		playlist_norm = defaultdict(float)			#{pid: norm^2 of vector}
		playlist_topics = defaultdict(set)			#{pid:set(topics)}
		for pid in pid_topics.keys():
			for topic,prob in pid_topics[pid].items():
				playlist_norm[pid] += prob*prob
				playlist_topics[pid].add(topic)

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
				sim_playlist_dict[vid] = sum_prod / np.sqrt(playlist_norm[pid]*playlist_norm[vid])
		
			#Sorting sim_playlist_dict
			sorted_sim_playlist = sorted(sim_playlist_dict.items(),key=lambda x:x[1],reverse=True)[:top_pl_k]
			self.playlist_similarity[pid]=sorted_sim_playlist
			
			data_in_json = json.dumps(sorted_sim_playlist)
			fin.write("%s\t%s\n"%(pid,data_in_json))
		
		fin.close()	
		time_ed = time.time()
		self.cost_time = time_ed-time_st

def main():
	input_file = '/data/micolin/thesis-git/wangyiMusic/data/playlist_basic_info/playlist.basic_info_all'
	dataset = Dataset()
	dataset.build_dataset(input_file,10000)
	logging.info("Build dataset cost:%s"%(dataset.cost_time))
	playlistLDA = PlaylistLDA()
	playlistLDA.build_model(dataset)
	logging.info('Building lad-model cost:%s'%(playlistLDA.cost_time))
	playlist_sim_file = './playlist_similarity.json'
	playlistLDA.build_playlist_similarity(playlist_sim_file)
	logging.info('Building playlist_similarity cost:%s'%(playlistLDA.cost_time))

if __name__=="__main__":
	logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO,filename='./log/log.musicLDA')
	main()
