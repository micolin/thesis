#coding=utf8
import sys,os
from models import BaseModel,BaseDataSet
from recsys.datamodel.data import Data
from recsys.algorithm.factorize import SVD
import time,json
import logging

class SVDModel(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
	
	def build_model(self,uids,kn):
		data = Data()
		for uid,songs in uids.items():
			for song in songs:
				data.add_tuple((1,song,uid))
		svd = SVD()
		svd.set_data(data)
		svd.compute(k=kn,min_values=1)
		self.model = svd

	def recommend(self,uids):
		for uid in uids.keys():
			song_list = self.model.recommend(uid,n=300,only_unknowns=False,is_row=False)
			song_rec = [song[0] for song in song_list]
			print "%s\t%s"%(uid,json.dumps(song_rec))	#输出top_n推荐结果到文件


def main():
	args = sys.argv
	set_level = args[1]
	train_prob = args[2]
	kn = int(args[3])
	
	#File path config
	file_template = './song_dataset/user_dataset_%s_%s_%s'	#set_num,type,train_prob
	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test',train_prob)

	#Build dataset
	dataset = BaseDataSet()
	dataset.build_data(train_file,test_file)
	logging.info("Build dataset cost:%s"%(dataset.cost_time))
	
	#Initiate Recommender
	recommender = SVDModel()
	recommender.build_model(dataset.train_data,kn)
	recommender.recommend(dataset.train_data)

if __name__=="__main__":
	main()
