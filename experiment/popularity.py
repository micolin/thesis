#coding=utf8
import os,sys
from models import BaseModel,BaseDataSet
from collections import *
import time,json
import logging

class Popularity(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
		self.popular_list = []
	
	def recommend(self,uids,n):
		'''
		@params[in] uids: {uid: favor_songs}
		@params[in] n: int, recommend top_n
		'''
		time_begin = time.time()
		
		song_count = defaultdict(int)
		for songlist in uids.values():
			for song in songlist:
				song_count[song]+=1
		
		pop_list = sorted(song_count.items(),key=lambda x:x[1],reverse=True)
		self.popular_list = pop_list
		recommend_list = [song[0] for song in pop_list[:n]]
		for uid in uids.keys():
			print "%s\t%s"%(uid,json.dumps(recommend_list))	#输出top_n推荐结果到文件
				
		time_end = time.time()
		self.cost_time = time_end - time_begin
	
	def get_poplist(self,n):
		return self.popular_list[:n]

def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	dataset = BaseDataSet()
	file_template = './song_dataset/user_dataset_%s_%s_%s'	#set_levle,type,train_prob

	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test',train_prob)
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s",dataset.cost_time)

	#Initiate Recommender
	recommender = Popularity()
	recommender.recommend(dataset.train_data,500)
	logging.info("Train_prob:%s cost:%s"%(train_prob,recommender.cost_time))

if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/popularity.log',filemode='w')
	main()
