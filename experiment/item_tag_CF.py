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
		st_time = time.time()
		if os.path.exists(item_tag_file):
			self.load_ITDistribution(item_tag_file)
			return

		logging.info("File %s doesn't exist, building Item-Tag distribution, input:%s"%(item_tag_file,input_file))
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
		
		logging.info("Dumping item-tag distribution to file:%s"%(item_tag_file))
		with open(item_tag_file,'wb') as fin:
			data_in_json = json.dumps(self.song_tag_distrib)
			fin.write(data_in_json)
		logging.info("Dumping process done..")
		
		ed_time = time.time()
		self.cost_time = ed_time-st_time

	def load_ITDistribution(self,item_tag_file):
		logging.info('Loading item-tag distribution from file:%s'%(item_tag_file))
		time_st = time.time()
		input_file = open(item_tag_file,'rb')
		self.song_tag_distrib = json.loads(input_file.read())
		input_file.close()
		time_ed = time.time()
		self.cost_time = time_ed - time_st
		logging.info('Loading item-tag distribution done..')

	def build_item_similarity(self,all_songs,item_tag_file,item_sim_file,top_item_k=500):
		time_st = time.time()
		song_norm = defaultdict(float)
		for song in all_songs:
			try:
				for tag,num in self.song_tag_distrib[song].items():
					song_norm[song] += num*num
			except:
				song_norm[song] = 1

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
					inter_tag = set(self.song_tag_distrib[sid]) & set(self.song_tag_distrib[vid])
					for tag in inter_tag:
						sum_prod += self.song_tag_distrib[sid][tag] * self.song_tag_distrib[vid][tag]
					sim_song_dict[vid] = sum_prod / np.sqrt(song_norm[sid]*song_norm[vid])
				except:
					sim_song_dict[vid] = 0
			
			#Sorting sim_song_dict
			sorted_sim_song = sorted(sim_song_dict.items(),key=lambda x:x[1],reverse=True)
			self.item_similarity[sid] = sorted_sim_song[:top_item_k]

			data_in_json = json.dumps(sorted_sim_song)
			fin.write("%s\t%s\n"%(sid,data_in_json))

		fin.close()
		time_ed = time.time()
		self.cost_time = time_ed - time_st

	def load_item_similarity(self,item_sim_file,top_item_k=500):
		time_st = time.time()
		with open(item_sim_file,'rb') as fin:
			for line in fin.readlines():
				line = line.strip().split('\t')
				sid = line[0]
				sim_songs = json.loads(line[1])[:top_item_k]
				self.item_similarity[sid]=sim_songs
		time_ed = time.time()
		self.cost_time = time_ed - time_st

def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	dataset = BaseDataSet()
	file_template = './dataset/user_dataset_%s_%s_%s'	#set_num,type,train_prob
	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test',train_prob)
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s"%(dataset.cost_time))
	print "DataForTrain: %s"%(train_file)
	print "DataForTest: %s"%(test_file)
	print "Dataset train_set info: %s"%(dataset.get_train_info())
	print "Dataset test_set info: %s"%(dataset.get_test_info())

	playlist_file = '/data/micolin/thesis-git/wangyiMusic/data/playlist_basic_info/playlist.basic_info_all'
	item_tag_file = './mid_data/song_tag_distribution.json'
	recommender = ItemTagCF()
	recommender.build_ITDistribution(playlist_file,item_tag_file)
	item_sim_file = './mid_data/item_similarity_usingTag_%s_%s.json'%(set_level,train_prob)
	if os.path.exists(item_sim_file):
		logging.info("File %s exists, loading item similarity matrix"%(item_sim_file))
		recommender.load_item_similarity(item_sim_file)
		logging.info("Load item_similarity cost: %s"%(recommender.cost_time))
	else:
		logging.info("File %s doesn't exist, building item similarity matrix"%(item_sim_file))
		recommender.build_item_similarity(list(dataset.all_songs),item_tag_file,item_sim_file)
		logging.info("Load item_similarity cost: %s"%(recommender.cost_time))
	
	#ItemTagDistributer = ItemTagDistribution(item_tag_file,input_file)
	#logging.info('Item_tag cost:%s'%(ItemTagDistributer.cost_time))

if __name__=="__main__":
	#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/it_CF.log')
	main()
