#coding=utf8
import os,sys
import time
from collections import *
from models import BaseModel, BaseDataSet
import logging,json

class ItemCF(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
		self.item_similarity = {} # {itemid:{sim_item:similarity}}

	def build_item_similarity(self,uids,item_sim_file):
		'''
		@Desc: building item similarity matrix
		@params[in] uids: {uid: [favor_songid,]}
		@params[in] item_sim_file: path to save user_similarity matrix
		@[output] item_similarity json to file
		'''
		time_st = time.time()

		song_interUser = defaultdict(dict)
		song_user = defaultdict(int)
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
				item_sim[song][sid] = inter_num / np.sqrt(user_song[song]*user_song[sid])

		print len(item_sim)

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
	
	itemCF_recommender = ItemCF()
	item_sim_file = './dataset/item_similarity_%s_%s.json'%(set_level,train_prob)
	if os.path.exists(item_sim_file):
		logging.info("File %s exists, loading item similarity matrix"%(item_sim_file))
		itemCF_recommender.load_item_similarity(item_sim_file)
		logging.info("Load user_similarity cost: %s"%(itemCF_recommender.cost_time))
	else:
		logging.info("File %s doesn't exist, building item similarity matrix"%(item_sim_file))
		itemCF_recommender.build_item_similarity(dataset.train_data,item_sim_file)
		logging.info("Load user_similarity cost: %s"%(itemCF_recommender.cost_time))
	

if __name__=="__main__":
	#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/itemCF.log')
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	logging.info("ItemCF >>>>>>>>>>>> Start")
	main()
	logging.info("ItemCF >>>>>>>>>>>> Complete")
