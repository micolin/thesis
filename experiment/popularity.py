#coding=utf8
import os,sys
from models import BaseModel,BaseDataSet
from collections import *
import time
import logging

class Popularity(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
	
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
		
		popular_list = sorted(song_count.items(),key=lambda x:x[1],reverse=True)
		recommend_list = [song[0] for song in popular_list[:n]]
		for uid in uids.keys():
			self.result[uid] = recommend_list
				
		time_end = time.time()
		self.cost_time = time_end - time_begin
	
	def get_time(self):
		return self.cost_time

def main():
	args = sys.argv
	train_prob = float(args[1])
	rs_recommender = Popularity()
	dataset = BaseDataSet()
	dataset.build_data('./dataset/user_dataset_1w_train_'+str(train_prob),'./dataset/user_dataset_1w_test_'+str(train_prob))
	logging.info("Build dataset cost:%s",dataset.cost_time)
	print "Dataset train_set info: %s"%(dataset.get_train_info())
	print "Dataset test_set info: %s"%(dataset.get_test_info())
	for i in range(50,1000,50):
		rs_recommender.recommend(dataset.train_data,i)
		logging.info("Train_prob:%s Recommend Top_n:%s cost:%s"%(train_prob,i,rs_recommender.get_time()))
		print "Top_n:%s\tScores:%s"%(i,rs_recommender.score(dataset.test_data))
	
if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/popularity.log')
	main()
