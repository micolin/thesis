#coding=utf8
import os,sys
from collections import *
import logging,json
from models import BaseModel, BaseDataSet
from user_CF import UserCF
from userLDA import UserLDA

class HybirdModel(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
		self.user_similarity = defaultdict(dict)

	def Hybird_UserSim_Recommend(self,user_songs,userCF_sim_file, userLDA_sim_file):
		user_cf = UserCF()
		user_cf.load_user_similarity(userCF_sim_file)
		user_lda = UserLDA()
		user_lda.load_user_similarity(userLDA_sim_file)

	def Hybird_Song_Recommend(self,user_songs, userCF_sim_file, userLDA_sim_file):
		pass

def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	
	file_template = './song_dataset/user_dataset_%s_%s_%s' #set_level, type, train_prob
	userCF_sim_file = './song_dataset/mid_data/user_sim_%s_%s.json'%(set_level,train_prob)
	topic_num = int(raw_input("User_LDA topic_num:"))
	userLDA_sim_file = './song_dataset/mid_data/user_sim_with_lda_%s_%s_%s.json'%(set_level,train_prob,topic_num)
	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test', train_prob)
	
	#Build dataset
	dataset = BaseDataSet()
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s"%(dataset.cost_time))
	print "DataForTrain: %s"%(train_file)
	print "DataForTest: %s"%(test_file)
	print "Dataset train_set info: %s"%(dataset.get_train_info())
	print "Dataset test_set info: %s"%(dataset.get_test_info())

	#Build Hybird-Model
	recommender = HybirdModel()
	recommender.Hybird_UserSim_Recommend(dataset.train_data,userCF_sim_file,userLDA_sim_file)

if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	main()
