#coding=utf8
import os,sys
import time
from collections import *
import json

class BaseModel(object):
	def __init__(self):
		self.result = {}
		self.cost_time = 0
	def score(self,test_set):
		'''
		@Desc: measure precision, recall and f_score of recommendation
		@params[in] test_set: BaseDataSet.test_data, {uid:[songid,]}
		@return[out] score: dict, {precision:pre, recall: rc, f_score: f_s}
		'''
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

class BaseDataSet(object):
	'''
	@Desc: used for Popularity Model, Random-Select Model, userCF Model
	'''
	def __init__(self):
		self.train_data = {}	#{uid:[songid,]}
		self.test_data = {}		#{uid:[songid,]}
		self.all_songs = set()
		self.song_tag = {}		#
		self.user_tag = {}
		self.cost_time = 0
	
	def build_data(self,train_file,test_file):
		'''
		@Desc:
		@params[in] train_file: path of training file
		@params[in] test_file: path of testing file
		'''
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
	
	def load_song_tag_distribution(self,song_tag_file):
		'''
		@Desc: load song_tag_distribution from file
		@params[in] song_tag_file: filepath of song_tag distr file, json
		'''
		time_st = time.time()
		with open(song_tag_file,'rb') as fin:
			self.song_tag = json.loads(fin.read())
		time_ed = time.time()
		self.cost_time = time_ed - time_st

	def load_user_tag_distribution(self,user_tag_file):
		'''
		@Desc: load user_tag_distribution from file
		@params[in] user_tag_file: filepath of song_tag distr file, json
		'''
		time_st = time.time()
		with open(user_tag_file,'rb') as fin:
			self.user_tag = json.loads(fin.read())
		time_ed = time.time()
		self.cost_time = time_ed - time_st

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
		info['songs_tot'] = len(self.all_songs)
		info['max'] = max(size_list)
		info['min'] = min(size_list)
		info['average'] = sum(size_list)/len(size_list)
		return info

import heapq
class TopKHeap(object):
	def __init__(self,k):
		self.k = k
		self.data = []

	def push(self,elem):
		_elem = (elem[1],elem[0])
		if len(self.data) < self.k:
			heapq.heappush(self.data,_elem)
		else:
			topk_small = self.data[0]
			if _elem[0] > topk_small[0]:
				heapq.heapreplace(self.data,_elem)

	def topk(self):
		'''
		@Desc: Get top-k elems
		'''
		return [(x[1],x[0]) for x in sorted([heapq.heappop(self.data) for i in range(len(self.data))],key=lambda x:x[0],reverse=True)]

import random

def dot(u,v):
    return sum(ux*vx for ux,vx in zip(u,v))

class LSH_Cosine(object):
	def __init__(self,d):
		self.d = d
	
	def rand_vec(self):
		return [random.gauss(0,1) for i in range(self.d)]

	def create_hash_func(self):
		return CosineHash(self.rand_vec())
	
	def combine(self,hashes):
		return sum(2**i if h > 0 else 0 for i,h in enumerate(hashes))

class CosineHash(object):
	def __init__(self,r):
		self.r = r

	def hash(self,vec):
		return self.sgn(dot(vec,self.r))

	def sgn(self,x):
		return int(x>0)

def test():
	lsh_cosine = LSH_Cosine(10)
	print lsh_cosine.rand_vec()

#test()
