#coidng=utf8
import config
import os,sys
from collections import *
from pymongo import Connection
import logging
import random

def db_connection():
	'''
	@desc: get mongodb connection
	@return[out] object of db connection
	'''
	logging.info('Connect to database @%s:%s'%(config.db_host,config.db_port))
	conn = Connection(config.db_host,config.db_port)
	db = conn.easyNetMusic
	return db

def select_uid_reservoir(filepath,max_num):
	'''
	@desc: select userid for training and testing with reservoir simpling
	@params[in] filepath : path of idfile
	@params[in] max_num : limitation of selection
	@return[out]
	'''
	selected_uid = []
	with open(filepath,'r') as fin:
		for idx,line in enumerate(fin.readlines()):
			uid = line.strip()
			if len(selected_uid)<max_num:
				selected_uid.append(uid)
			else:
				rand = random.randint(0,idx)
				if rand < max_num:
					selected_uid[rand]=uid
	return selected_uid

def build_dataset(filepath,max_num,train_prop=0.9):
	uid_list = select_uid_reservoir(filepath,max_num)
	seper_idx = int(max_num * train_prop)
	train_set = set(uid_list[:seper_idx])
	test_set = set(uid_list[seper_idx:])
	print train_set
	print test_set
	return train_set,test_set
	

if __name__=="__main__":
	args = sys.argv
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	#build_dataset('../wangyiMusic/data/user_info/user_id_all',10000)
	print globals()['build_dataset']('../wangyiMusic/data/user_info/user_id_all',10000)
