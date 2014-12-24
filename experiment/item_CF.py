#coding=utf8
import os,sys
import time
from collections import *
from models import BaseModel, BaseDataSet
import logging

class ItemCF(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
	
	def recommend(self,us_matrix, item_knn=5, top_n=10):
		pass
	
	def cos_sim(A,B):
		pass

def main():
	args = sys.argv
	set_num = args[1]
	train_prob = args[2]
	dataset = MatDataSet()
	file_template = './dataset/user_dataset_%sw_%s_%s'	#set_num,type,train_prob
	train_file = file_template%(set_num,'train',train_prob)
	test_file = file_template%(set_num,'test',train_prob)
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s"%(dataset.cost_time))
	print "DataForTrain: %s"%(train_file)
	print "DataForTest: %s"%(test_file)
	print "Dataset train_set info: %s"%(dataset.get_train_info())
	print "Dataset test_set info: %s"%(dataset.get_test_info())
	
	itemCF_recommender = ItemCF()
	

if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	main()
