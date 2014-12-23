#coding=utf8
import os,sys
from models import BaseModel,BaseDataSet
from collections import *
import time
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
			self.result[uid] = recommend_list
				
		time_end = time.time()
		self.cost_time = time_end - time_begin
	
	def get_time(self):
		return self.cost_time
	
	def get_poplist(self,n):
		return self.popular_list[:n]

def main():
	args = sys.argv
	set_num = args[1]
	train_prob = args[2]
	rs_recommender = Popularity()
	dataset = BaseDataSet()
	file_template = './dataset/user_dataset_%sw_%s_%s'	#set_num,type,train_prob
	train_file = file_template%(set_num,'train',train_prob)
	test_file = file_template%(set_num,'test',train_prob)
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s",dataset.cost_time)
	print "DataForTrain: %s"%(train_file)
	print "DataForTest: %s"%(test_file)
	print "Dataset train_set info: %s"%(dataset.get_train_info())
	print "Dataset test_set info: %s"%(dataset.get_test_info())
	for i in range(1,201):
		rs_recommender.recommend(dataset.train_data,i)
		logging.info("Train_prob:%s Recommend Top_n:%s cost:%s"%(train_prob,i,rs_recommender.get_time()))
		#logging.info("Top_10_song:%s"%(rs_recommender.get_poplist(10)))
		print "Top_n:%s\tScores:%s"%(i,rs_recommender.score(dataset.test_data))
	
if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/popularity.log')
	main()
