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
			#recommend_songs = [all_songs[i] for i in rand_select if all_song[i]]
			recommend_songs = [all_songs[i] for i in rand_select if all_songs[i] not in uids[uid]]
			self.result[uid] = recommend_songs
			
		time_end = time.time()
		self.cost_time = time_end - time_begin
	
	def get_result(self):
		return self.result

	def get_time(self):
		return self.cost_time

def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	e_type = args[3]	#Experiment type: song or playlist
	recommender = RandomSelect()
	dataset = BaseDataSet()
	file_template = './song_dataset/user_dataset_%s_%s_%s'	#set_level,type,train_prob
	if e_type == 'playlist':
		file_template = './pl_dataset/user_playlist_%s_%s_%s'	#set_level,type,train_prob
		
	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test',train_prob)
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s",dataset.cost_time)
	print "DataForTrain: %s"%(train_file)
	print "DataForTest: %s"%(test_file)
	print "Dataset train_set info: %s"%(dataset.get_train_info())
	print "Dataset test_set info: %s"%(dataset.get_test_info())
	best_f_score = {'f_score':0}
	best_precision = {'precision':0}
	best_recall = {'recall':0}
	for i in range(1,201):
		recommender.recommend(dataset.train_data,list(dataset.all_songs),i)
		logging.info("Train_prob:%s Recommend Top_n:%s cost:%s"%(train_prob,i,recommender.get_time()))
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
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/random_select.log',filemode='w')
	main()
