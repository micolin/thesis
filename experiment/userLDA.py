#coding=utf8
import os,sys
import logging
import time
import numpy as np
from models import BaseModel, BaseDataSet
from collections import *
import json
from gensim import corpora, models, similarities

class UserLDA(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
		self.dictionary = None
		self.model = None
		self.user_similarity = defaultdict(list)
	
	def build_model(self,uids,topic_num=100):
		pass

	def get_user_topic_distribution(self):
		pass
	
	def build_user_similarity(self,user_sim_file,uids,topic_num,top_user_k=500):
		pass

	def load_user_similarity(self,user_sim_file):
		pass

def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	topic_num = int(args[3])
	file_template = './song_dataset/user_dataset_%s_%s_%s' #set_level, type, train_prob
	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test',train_prob)
	
	dataset = BaseDataSet()
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s"%(dataset.cost_time))
	
	recommender = UserLDA()
	user_sim_file = './song_dataset/mid_data/user_sim_with_lda_%s_%s_%s.json'%(set_level,train_prob,topic_num)
	recommender.build_user_similarity(user_sim_file,dataset.train_data,topic_num=topic_num, top_user_k=500)

if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/playlistLDA.log',filemode='w')
	main()
