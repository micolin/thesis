#coding=utf8
import os,sys
import random
import time,json
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
			recommend_list = [all_songs[i] for i in rand_select if all_songs[i] not in uids[uid]]
			print "%s\t%s"%(uid,json.dumps(recommend_list))	#输出top_n推荐结果到文件
			
		time_end = time.time()
		self.cost_time = time_end - time_begin
	
	def get_time(self):
		return self.cost_time

def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	dataset = BaseDataSet()
	file_template = './song_dataset/user_dataset_%s_%s_%s'	#set_level,type,train_prob
		
	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test',train_prob)
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s",dataset.cost_time)

	recommender = RandomSelect()
	recommender.recommend(dataset.train_data,list(dataset.all_songs),500)
	logging.info("Train_prob:%s cost:%s"%(train_prob,recommender.get_time()))

if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/random_select.log',filemode='w')
	main()
