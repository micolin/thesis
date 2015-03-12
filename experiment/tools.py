#coding=utf8
import sys,os
import json
from collections import *
from userLDA import UserLDA
from models import BaseDataSet

def load_tags_dict(input_file='/data/micolin/thesis-git/wangyiMusic/data/cate.dict'):
	tags_dict = defaultdict(set)
	with open(input_file,'rb') as fin:
		for line in fin.readlines():
			line = line.strip().split('\t')
			tag = line[0]
			cate = line[1]
			tags_dict[cate].add(tag.decode('utf8'))
	return tags_dict

def norm_song_distrib(input_file):
	tags_dict=load_tags_dict()
	with open(input_file,'rb') as fin:
		for line in fin.readlines():
			line = line.strip().split('\t')
			sid = line[0]
			tags = json.loads(line[1])
			new_tags = {}
			for cate in tags_dict.keys():
				cate_sum = 0.0
				for tag in tags_dict[cate] & set(tags.keys()):
					cate_sum += tags[tag]
				for tag in tags_dict[cate] & set(tags.keys()):
					new_tags[tag]=float(tags[tag])/cate_sum
			print "%s\t%s"%(sid,json.dumps(new_tags))

def get_lda_topics(args):
	set_level = args[0]
	train_prob = args[1]
	topic_num = int(args[2])

	file_template = './song_dataset/user_dataset_%s_%s_%s' #set_level, type, train_prob
	train_file = file_template%(set_level,'train',train_prob)
	test_file = file_template%(set_level,'test',train_prob)
	
	dataset = BaseDataSet()
	dataset.build_data(train_file,test_file)

	recommender = UserLDA()
	recommender.build_model(dataset.train_data,topic_num)
	for idx,distrib in enumerate(recommender.model.print_topics(1000)):
		dist0 = distrib.split()[0].split('*')[0]
		if float(dist0) > 0:
			print "Topic#%s\t%s"%(idx,distrib)

def main():
	norm_song_distrib('./song_dataset/mid_data/song_tag_distribution.json')

if __name__=="__main__":
	args = sys.argv
	job = args[1]
	func = globals()[job]
	func(args[2:])
