#coding=utf8
import os,sys
import random
import time
from models import BaseModel,BaseDataSet
import logging

class RandomSelect(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
	
	def recommend(self,uids,all_songs,n):
		'''
		@params[in] uids: {uid: favor_songs}
		@params[in] all_songs: [songid,], contain all cadidate songs
		@params[in] n : int, recommend top_n
		'''
		time_begin = time.time()
			
		for uid in uids.keys():
			#Recommend process for each user
			rand_select = random.sample(xrange(0,len(all_songs)),n)
			recommend_songs = [all_songs[i] for i in rand_select]
			self.result[uid] = recommend_songs
			
		time_end = time.time()
		self.cost_time = time_end - time_begin
	
	def get_result(self):
		return self.result

	def get_time(self):
		return self.cost_time

def main():
	args = sys.argv
	set_num = args[1]
	train_prob = args[2]
	rs_recommender = RandomSelect()
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
		rs_recommender.recommend(dataset.train_data,list(dataset.all_songs),i)
		logging.info("Train_prob:%s Recommend Top_n:%s cost:%s"%(train_prob,i,rs_recommender.get_time()))
		print "Top_n:%s\tScores:%s"%(i,rs_recommender.score(dataset.test_data))

if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/random_select.log')
	main()
