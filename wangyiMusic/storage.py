#coding=utf-8
from collections import *
import os,sys
import logging
from pymongo import Connection
import config

def connect_to_db():
	logging.info('Connect to database @%s:%s'%(config.db_host,config.db_port))
	conn = Connection(config.db_host,config.db_port)
	db = conn.easyNetMusic
	return db

def song_to_db(filedir):
	db = connect_to_db()
	collection = db.song_info

	def file2db(collection,filepath):
		with open(filepath,'rb') as fin:
			data = {}
			for line in fin.readlines():
				line = line.split('\t')
				if line[0].isdigit():
					if data:
						collection.insert(data)
					data = {}
					data['_id'] = line[0]
					data['name'] = line[1]
					data['singer_id'] = line[2]
					data['singer_name'] = line[3]
					data['album_id'] = line[4]
					data['album_name'] = line[5]
					data['lrc'] = line[6]
					try:
						data['sim_songs'] = line[7]
					except:
						data['sim_songs'] = 'none'
				else:
					if len(line)==1:
						data['lrc']+=line[0].strip()
					elif len(line)==3:
						data['lrc']+=line[0].strip()
						data['sim_songs']=line[1]

	if os.path.isfile(filedir):
		logging.info('Saving file:%s'%(filedir))
		file2db(collection,filedir)
	else:
		for filepath in os.listdir(filedir):
			filepath = os.path.join(filedir,filepath)
			logging.info('Saving file:%s'%(filepath))
			file2db(collection,filepath)

def user_to_db(filedir):
	db = connect_to_db()
	collection = db.user_info
	
	def file2db(collection,filepath):
		with open(filepath,'rb') as fin :
			for line in fin.readlines():
				data = {}
				line = line.split('\t')
				data['_id'] = line[0]
				data['name'] = line[1]
				data['gender'] = line[2]
				data['area'] = line[3]
				data['expertTag'] = line[4]
				action = line[5][1:-1].split(',')
				data['event_num'] = int(action[0])
				data['follows_num'] = int(action[1])
				data['fans_num'] = int(action[2])
				data['fans'] = line[7]
				data['follows'] = line[8]
				data['favor_playlist'] = line[9]
				collection.insert(data)
				

	if os.path.isfile(filedir):
		logging.info('Saving file:%s'%(filedir))
		file2db(collection,filedir)
	else:
		for filepath in os.listdir(filedir):
			filepath = os.path.join(filedir,filepath)
			logging.info('Saving file:%s'%(filepath))
			file2db(collection,filepath)

def playlist_to_db(filedir):
	db = connect_to_db()
	collection = db.playlist_info

	def file2db(collection,filepath):
		with open(filepath,'rb') as fin:
			for line in fin.readlines():
				data = {}
				line = line.strip().split('\t')
				data['_id'] = line[0]
				data['name'] = line[1]
				data['creator'] = line[2]
				data['favor_num'] = line[3]
				data['share_num'] = line[4]
				data['comment_num'] = line[5]
				data['tags'] = line[6]
				data['desc'] = line[7]
				data['play_times'] = line[8]
				data['sim_playlists'] = line[9]
				data['songs'] = line[11]
				collection.insert(data)

	if os.path.isfile(filedir):
		logging.info("Saving file:%s"%(filedir))
		file2db(collection,filedir)
	else:
		for filepath in os.listdir(filedir):
			filepath = os.path.join(filedir,filepath)
			logging.info("Saving file:%s"%(filedir))
			file2db(collection,filepath)

def user_favor_to_db(filedir):
	db = connect_to_db()
	inputfile = os.path.basename(filedir)
	file_date = inputfile.split('_')[-1]
	collection = db['user_favor_'+file_date]
	
	def file2db(collection,filepath):
		with open(filepath,'rb') as fin:
			for idx,line in enumerate(fin.readlines()):
				data = {}
				line = line.strip().split('\t')
				data['_id'] = line[0]
				try:
					data['favor_songs'] = line[1]
				except:
					data['favor_songs'] = None
				collection.insert(data)
	
	logging.info("Saving file:%s"%(input_dir))
	file2db(collection,filedir)

if __name__=="__main__":
	args = sys.argv
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	job = args[1]
	try:
		func = globals()[job]
		input_dir = args[2]
		func(input_dir)
	except Exception,e:
		logging.error("Error occur. Please check.")
		logging.error(e)
