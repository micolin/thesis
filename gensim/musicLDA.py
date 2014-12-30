#coding=utf8
import os,sys
import logging
import time
from collections import *
import json
from gensim import corpora, models, similarities

class Playlist:
	def __init__(self,pid,songs,tags,hot):
		self.pid = pid
		self.songlist = songs
		self.hot = 0
		self.tag = tags

class Dataset:
	def __init__(self):
		self.playlists = []
		self.cost_time = 0

	def build_dataset(self,input_path,hot_theta,top_n):
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
		self.pids = []
		self.cost_time = 0

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
		corpus = [song_dictionary.doc2bow(playlist) for playlist in self.playlists]
		logging.info('Transform corpus using tfidf model')
		tfidf = models.TfidfModel(corpus)
		corpus_tfidf = tfidf[corpus]
		logging.info("Training lda model with corpus")
		self.model = models.ldamodel.LdaModel(corpus_tfidf,num_topics=40,id2word=song_dictionary)
		logging.info("Model training done..")
		time_ed = time.time()
		self.cost_time = time_ed - time_st

def main():
	input_file = '/data/micolin/thesis-git/wangyiMusic/data/playlist_basic_info/playlist.basic_info_all'
	dataset = Dataset()
	dataset.build_dataset(input_file,10000,10)
	logging.info("Build dataset cost:%s"%(dataset.cost_time))
	playlistLDA = PlaylistLDA()
	playlistLDA.build_model(dataset)
	logging.info('Building lad-model cost:%s'%(playlistLDA.cost_time))

if __name__=="__main__":
	logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO,filename='log.musicLDA')
	main()
