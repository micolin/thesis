#coding=utf8
import sys,os
import json
from collections import *

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

def main():
	norm_song_distrib('./song_dataset/mid_data/song_tag_distribution.json')
