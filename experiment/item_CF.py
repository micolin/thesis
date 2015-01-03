#coding=utf8
import os,sys
import time
from collections import *
import numpy as np
from models import BaseModel, BaseDataSet
import logging,json

class ItemCF(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
		self.item_similarity = {} # {itemid:[(sim_item,similarity)]} sorted by similarity

	def build_item_similarity(self,uids,item_sim_file):
		'''
		@Desc: building item similarity matrix
		@params[in] uids: {uid: [favor_songid,]}
		@params[in] item_sim_file: path to save item_similarity matrix
		@[output] item_similarity json to file
		'''
		time_st = time.time()

		song_interUser = defaultdict(dict)	#{song:{sim_song:inter_num}}
		song_user = defaultdict(int)		#number of user like each song
		for uid, song_list in uids.iteritems():
			for s in range(len(song_list)):
				song_user[song_list[s]] += 1
				for v in range(len(song_list)):
					if v == s:
						continue
					try:
						song_interUser[song_list[s]][song_list[v]] += 1
					except:
						song_interUser[song_list[s]][song_list[v]] = 1
		
		item_sim = defaultdict(dict)
		for song, sim_songs in song_interUser.items():
			for sid, inter_num in sim_songs.iteritems():
				item_sim[song][sid] = inter_num / np.sqrt(song_user[song]*song_user[sid])
		
		#Sorting item_similarity list 
		logging.info('Sorting similarity result..')
		self.item_similarity = defaultdict(list)
		for song in item_sim.keys():
			self.item_similarity[song] = sorted(item_sim[song].items(),key=lambda x:x[1],reverse=True)

		#Dumping item_similarity matrix to file
		logging.info('Dumping item_similarity matrix to file:%s'%(item_sim_file))
		data_in_json = json.dumps(self.item_similarity)
		with open(item_sim_file,'wb') as fin:
			fin.write(data_in_json)
		logging.info('Dumping process done.')

		time_ed = time.time()
		self.cost_time = time_ed - time_st	

	def load_item_similarity(self,item_sim_file):
		'''
		@Desc: load item similarity matrix from file
		@params[in] item_sim_file: file of item_similarity json 
		'''
		time_st = time.time()
		input_file = open(item_sim_file,'rb')
		self.item_similarity = json.loads(input_file.read())
		input_file.close()
		time_ed = time.time()
		self.cost_time = time_ed - time_st

	def recommend(self,uids, item_k=5, top_n=10):
		'''
		@Desc: main process of recommendation
		@params[in] uids: {uid:[favor_songid,]}
		@params[in] item_k: use top_k similar songs to recommend
		@params[in] top_n: recommend top_n songs to user
		'''
		time_st = time.time()
		for uid in uids.keys():
			candidate_songs = defaultdict(float)
			remove_sid = set(uids[uid])
			for songid in uids[uid]:
				item_cnt = 0
				for (sim_song,sim) in self.item_similarity[songid]:
					if item_cnt >= item_k:
						break
					if sim_song in remove_sid:
						continue
					else:
						candidate_songs[sim_song] += sim
						item_cnt +=1

			top_n_songs = sorted(candidate_songs.items(),key=lambda x:x[1],reverse=True)[:top_n]
			self.result[uid] = [song[0] for song in top_n_songs]

		time_ed = time.time()
		self.cost_time = time_ed - time_st	
	
def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	e_type = args[3]	#Experiment type: song or playlist
	dataset = BaseDataSet()
	file_template = './song_dataset/user_dataset_%s_%s_%s'	#set_num,type,train_prob
	item_sim_file = './song_dataset/mid_data/item_similarity_%s_%s.json'%(set_level,train_prob)
	if e_type == 'playlist':
		file_template = './pl_dataset/user_playlist_%s_%s_%s'	#set_num,type,train_prob
		item_sim_file = './pl_dataset/mid_data/item_similarity_%s_%s.json'%(set_level,train_prob)
		
	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test',train_prob)
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s"%(dataset.cost_time))
	print "DataForTrain: %s"%(train_file)
	print "DataForTest: %s"%(test_file)
	print "Dataset train_set info: %s"%(dataset.get_train_info())
	print "Dataset test_set info: %s"%(dataset.get_test_info())
	
	#Record best scores
	best_f_score = {'f_score':0}
	best_precision = {'precision':0}
	best_recall = {'recall':0}

	itemCF_recommender = ItemCF()
	if os.path.exists(item_sim_file):
		logging.info("File %s exists, loading item similarity matrix"%(item_sim_file))
		itemCF_recommender.load_item_similarity(item_sim_file)
		logging.info("Load item_similarity cost: %s"%(itemCF_recommender.cost_time))
	else:
		logging.info("File %s doesn't exist, building item similarity matrix"%(item_sim_file))
		itemCF_recommender.build_item_similarity(dataset.train_data,item_sim_file)
		logging.info("Load item_similarity cost: %s"%(itemCF_recommender.cost_time))
	
	#Recommendation
	for item_k in range(20,70):
		for top_n in range(1,80,2):
			itemCF_recommender.recommend(dataset.train_data,item_k=item_k,top_n=top_n)
			logging.info("Train_prob:%s Item_k:%s Top_n:%s Cost:%s"%(train_prob,item_k,top_n,itemCF_recommender.cost_time))
			scores = itemCF_recommender.score(dataset.test_data)
			print "Item_k:%s\tTop_n:%s\tScores:%s"%(item_k,top_n,scores)

			#Find Best Score
			if scores['f_score'] > best_f_score['f_score']:
				best_f_score = scores
				best_f_score['item_k'] = item_k
				best_f_score['top_n'] = top_n
			if scores['precision'] > best_precision['precision']:
				best_precision = scores
				best_precision['item_k']=item_k
				best_precision['top_n'] = top_n
			if scores['recall'] > best_recall['recall']:
				best_recall = scores
				best_recall['item_k']=item_k
				best_recall['top_n'] = top_n
	
	print "Best_F_Score: %s"%(best_f_score)
	print "Best_Precision: %s"%(best_precision)
	print "Best_Recall: %s"%(best_recall)

if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/itemCF.log',filemode='w')
	#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	logging.info("ItemCF >>>>>>>>>>>> Start")
	main()
	logging.info("ItemCF >>>>>>>>>>>> Complete")
