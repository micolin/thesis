#coding=utf8
import os,sys
import time
from collections import *

class BaseModel:
	def __init__(self):
		self.result = {}
		self.cost_time = 0
	def score(self,test_set):
		hit = 0
		predict_tot = 0
		recall_tot = 0
		for uid, predict_songs in self.result.iteritems():
			test_songs = test_set[uid]
			hit += len(set(predict_songs) & set(test_songs))
			predict_tot += len(predict_songs)
			recall_tot += len(test_songs)
		
		precision = float(hit)/predict_tot
		recall = float(hit)/recall_tot
		if precision==0 and recall == 0:
			fscore = 0.0
		else:
			fscore = 2.0*(precision*recall)/(precision+recall)
		scores = {'precision':precision,'recall':recall,'f_score':fscore}
		return scores

class BaseDataSet:
	'''
	@Desc: used for Popularity Model and Random-Select Model
	'''
	def __init__(self):
		self.train_data = {}	#{uid:[songid,]}
		self.test_data = {}		#{uid:[songid,]}
		self.all_songs = set()
		self.cost_time = 0
	
	def build_data(self,train_file,test_file):
		build_begin = time.time()
		with open(train_file,'rb') as fin:
			for line in fin.readlines():
				line = line.strip().split('\t')
				uid = line[0]
				songs = line[1].split(',')
				self.train_data[uid] = songs
				self.all_songs.update(songs)
	
		with open(test_file,'rb') as fin:
			for line in fin.readlines():
				line = line.strip().split('\t')
				self.test_data[line[0]] = [song for song in line[1].split(',') if song in self.all_songs]
		build_end = time.time()
		self.cost_time = build_end-build_begin
	
	def get_test_info(self):
		size_list = [len(songs) for songs in self.test_data.values()]
		info = {}
		info['max'] = max(size_list)
		info['min'] = min(size_list)
		info['average'] = sum(size_list)/len(size_list)
		return info

	def get_train_info(self):
		size_list = [len(songs) for songs in self.train_data.values()]
		info = {}
		info['max'] = max(size_list)
		info['min'] = min(size_list)
		info['average'] = sum(size_list)/len(size_list)
		return info

import numpy as np
class MatDataSet(BaseDataSet):
	def __init__(self):
		BaseDataSet.__init__(self)	#Include member : train_data, test_data, cost_time, all_songs
		self.us_matrix = []
		self.song_user_dict = defaultdict(list)
		self.user_dict = {}
		self.song_dict = {}

	def build_data(self,train_file,test_file):
		build_st = time.time()
		BaseDataSet.build_data(self,train_file,test_file)
		user_tot = len(self.train_data.keys())
		song_tot = len(self.all_songs)
		self.us_matrix = np.zeros((user_tot,song_tot),dtype='int8')
		
		#Record song-idx mapping
		for idx,song in enumerate(self.all_songs):
			self.song_dict[song] = idx
		#Record user-idx mapping
		for idx,uid in enumerate(self.train_data.iterkeys()):
			self.user_dict[uid] = idx
			for song in self.train_data[uid]:
				self.us_matrix[idx][self.song_dict[song]] = 1
		self.us_matrix = np.mat(self.us_matrix)
		build_ed = time.time()
		self.cost_time = build_ed - build_st

def test():
	dataset = MatDataSet()
	dataset.build_data('./dataset/user_dataset_1w_train_0.6','./dataset/user_dataset_1w_test_0.6')
	print "User_dict:%s"%(dataset.user_dict)
	print "Cost_time:",(dataset.cost_time)

#test()
