#coding=utf8
import os,sys
from collections import *
import time
import numpy as np
from models import BaseModel, BaseDataSet
import logging,json

class ItemTagCF(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
		self.item_similarity = defaultdict(dict)
		self.song_tag_distrib = defaultdict(dict)

	def build_ITDistribution(self,input_file,item_tag_file):
		'''
		@Desc: build item-tag distribution from input_file
		@params[in]: input_file: path of file which contains item and tag infomation
		@params[in]: item_tag_file: path of output
		'''
		#Load item-tag distribution if item_tag_file exists
		if os.path.exists(item_tag_file):
			self.load_ITDistribution(item_tag_file)
			return
		
		#Build item-tag distribution
		logging.info("File %s doesn't exist, building Item-Tag distribution, input:%s"%(item_tag_file,input_file))
		st_time = time.time()
		with open(input_file,'rb') as fin:
			for line in fin.readlines():
				line = line.strip().split('\t')
				if line[6] == "none":
					continue
				tags = line[6].split(',')
				for song in line[11].split(','):
					for tag in tags:
						try:
							self.song_tag_distrib[song][tag] += 1
						except:
							self.song_tag_distrib[song][tag] = 1
		
		#Dump item-tag distribution to file
		logging.info("Dumping item-tag distribution to file:%s"%(item_tag_file))
		with open(item_tag_file,'wb') as fin:
			data_in_json = json.dumps(self.song_tag_distrib)
			fin.write(data_in_json)
		logging.info("Dumping process done..")
		
		ed_time = time.time()
		logging.info('Build item-tag distribution cost:%s'%(time_ed - time_st))

	def load_ITDistribution(self,item_tag_file):
		'''
		@Desc: load item-tag distribtion from file
		@params[in] item_tag_file: path of file contains item-tag distribution
		'''
		logging.info('Loading item-tag distribution from file:%s'%(item_tag_file))
		time_st = time.time()
		input_file = open(item_tag_file,'rb')
		self.song_tag_distrib = json.loads(input_file.read())
		input_file.close()
		time_ed = time.time()
		logging.info('Load item-tag distribution cost:%s'%(time_ed - time_st))

	def build_item_similarity(self,all_songs,item_sim_file,top_item_k=500):
		'''
		@Desc: build item-similarity matrix for all item
		@params[in] all_songs: list, [sid, ]
		@params[in]	item_sim_file: path of file contains item-similarity matrix
		@params[in] top_item_k: number of sim-user to be kept in item-similarity matrix
		'''
		#Load item-similarity matrix from file if item_sim_file exsits
		if os.path.exists(item_sim_file):
			self.load_item_similarity(item_sim_file)
			return
		
		#Build item-similarity matrix
		time_st = time.time()
	
		#Calculate nomalization of each song
		song_norm = defaultdict(float)
		for song in all_songs:
			try:
				for tag,num in self.song_tag_distrib[song].items():
					song_norm[song] += num*num
			except:
				song_norm[song] = 1

		#Calculate sim_songs for each song
		songs_num = len(all_songs)
		fin = open(item_sim_file,'w')
		for idx,sid in enumerate(all_songs):
			logging.info('Calculating similarity of sid:%s #%s of %s'%(sid,idx,songs_num))
			sim_song_dict = defaultdict(float)
			for vid in all_songs:
				if sid == vid:
					continue
				sum_prod = 0
				try:
					inter_tag = set(self.song_tag_distrib[sid].keys()) & set(self.song_tag_distrib[vid].keys())
					#There's no inter_tag, similarity will be zero, pass
					if len(inter_tag) == 0:
						continue
					for tag in inter_tag:
						sum_prod += self.song_tag_distrib[sid][tag] * self.song_tag_distrib[vid][tag]
					sim_song_dict[vid] = sum_prod / np.sqrt(song_norm[sid]*song_norm[vid])
				except:
					pass
			
			#Sorting sim_song_dict
			sorted_sim_song = sorted(sim_song_dict.items(),key=lambda x:x[1],reverse=True)[:top_item_k]
			self.item_similarity[sid] = sorted_sim_song
			
			#Dump to file
			data_in_json = json.dumps(sorted_sim_song)
			fin.write("%s\t%s\n"%(sid,data_in_json))

		fin.close()
		time_ed = time.time()
		logging.info("Build item-similarity cost: %s"%(time_ed-time_st))

	def load_item_similarity(self,item_sim_file):
		'''
		@Desc: load item-similarity matrix from file	
		@params[in] item_sim_file: path of file which contains item-similarity info
		'''
		time_st = time.time()
		with open(item_sim_file,'rb') as fin:
			for line in open(item_sim_file,'rb'):
				line = fin.readline()
				line = line.strip().split('\t')
				sid = line[0]
				sim_songs = json.loads(line[1])
				self.item_similarity[sid]=sim_songs
		time_ed = time.time()
		logging.info("Load item-similarity from file cost: %s"%(time_ed-time_st))

	def recommend(self,uids, item_k=5, top_n=10):
		'''
		@Desc: recommend items to all user
		@params[in] item_k: int, calculate k-nn item to recommend
		@params[in] top_n: int, number of final recommendation
		'''
		time_st = time.time()
		for uid in uids.keys():
			candidate_songs = defaultdict(float)
			remove_sid = set(uids[uid])
			for songid in uids[uid]:
				item_cnt = 0
				try:
					for (sim_song,sim) in self.item_similarity[songid]:
						if item_cnt >= item_k:
							break
						if sim_song in remove_sid:
							continue
						else:
							candidate_songs[sim_song] += sim
							item_cnt += 1
				except Exception,e:
					logging.error(e)
			top_n_songs = sorted(candidate_songs.items(),key=lambda x:x[1],reverse=True)[:top_n]
			self.result[uid] = [song[0] for song in top_n_songs]
		
		time_ed = time.time()
		self.cost_time = time_ed - time_st

def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	top_n = int(args[3])

	#Filepath config
	playlist_file = '/data/micolin/thesis-git/wangyiMusic/data/playlist_basic_info/playlist.basic_info_all'
	item_tag_file = './song_dataset/mid_data/song_tag_distribution.json'
	file_template = './song_dataset/user_dataset_%s_%s_%s'	#set_num,type,train_prob
	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test',train_prob)
	top_item_k=1000
	item_sim_file = './song_dataset/mid_data/item_similarity_withTag_%s_%s_%s.json'%(set_level,train_prob,top_item_k)
	
	#Build dataset
	dataset = BaseDataSet()
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s"%(dataset.cost_time))
	print "DataForTrain: %s"%(train_file)
	print "DataForTest: %s"%(test_file)
	print "Dataset train_set info: %s"%(dataset.get_train_info())
	print "Dataset test_set info: %s"%(dataset.get_test_info())

	#Initiate recommender
	recommender = ItemTagCF()
	recommender.build_ITDistribution(playlist_file,item_tag_file)
	recommender.build_item_similarity(list(dataset.all_songs),item_sim_file,top_item_k=top_item_k)
	
	#Record best scores
	best_f_score = {'f_score':0}
	best_precision = {'precision':0}
	best_recall = {'recall':0}

	#Recommendation
	for item_k in range(20,100):
		recommender.recommend(dataset.train_data,item_k=item_k,top_n=top_n)
		logging.info("Train_prob:%s Item_k:%s Top_n:%s Cost:%s"%(train_prob,item_k,top_n,recommender.cost_time))
		scores = recommender.score(dataset.test_data)
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
	#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/it_CF.log',filemode='w')
	main()
