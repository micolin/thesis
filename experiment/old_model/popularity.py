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
			self.result[uid] = [song for song in recommend_list if song not in uids[uid]]
				
		time_end = time.time()
		self.cost_time = time_end - time_begin
	
	def get_poplist(self,n):
		return self.popular_list[:n]

def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	e_type = args[3]	#Experiment type: song or playlist
	dataset = BaseDataSet()
	file_template = './song_dataset/user_dataset_%s_%s_%s'	#set_levle,type,train_prob
	if e_type == 'playlist':
		file_template = './pl_dataset/user_playlist_%s_%s_%s'	#set_levle,type,train_prob

	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test',train_prob)
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s",dataset.cost_time)
	print "DataForTrain: %s"%(train_file)
	print "DataForTest: %s"%(test_file)
	print "Dataset train_set info: %s"%(dataset.get_train_info())
	print "Dataset test_set info: %s"%(dataset.get_test_info())

	#Record best scores
	best_f_score = {'f_score':0}
	best_precision = {'precision':0}
	best_recall = {'recall':0}

	#Initiate Recommender
	recommender = Popularity()
	for i in [1,50,100,150,200]:
		recommender.recommend(dataset.train_data,i)
		logging.info("Train_prob:%s Recommend Top_n:%s cost:%s"%(train_prob,i,recommender.cost_time))
		#logging.info("Top_10_song:%s"%(recommender.get_poplist(10)))
		scores = recommender.score(dataset.test_data)
		print "Top_n:%s\tScores:%s"%(i,scores)

		#Find best scores
		if scores['f_score'] > best_f_score['f_score']:
			best_f_score = scores
			best_f_score['top_n'] = i
		if scores['precision'] > best_precision['precision']:
			best_precision = scores
			best_precision['top_n'] = i
		if scores['recall'] > best_recall['recall']:
			best_recall = scores
			best_recall['top_n'] = i
	
	print "Best_F_Score: %s"%(best_f_score)
	print "Best_Precision: %s"%(best_precision)
	print "Best_Recall: %s"%(best_recall)

if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/popularity.log',filemode='w')
	main()
