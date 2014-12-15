#coding=utf8
import urllib2
import os,sys
from lxml import etree
import logging
import json
from datetime import date
from user_info_crawler import get_page

class User:
	def __init__(self,user_id):
		self.user_id = user_id
		self.listenedSongs = self.__get_listenedSong()

	def __get_listenedSong(self):
		url_temp = 'http://music.163.com/user/listenedSongs/?id=%s'%(self.user_id)
		refer_url = 'http://music.163.com/user/home?id=%s'%(self.user_id)
		songs_json = get_page(url_temp,refer_url)
		listenedSongs = json.loads(songs_json)['listenedSongs']
		song_list = []
		for song in listenedSongs:
			song_id = str(song['id'])
			song_list.append(song_id)
		return song_list
	
	def data_in_string(self):
		return "%s\t%s"%(self.user_id,','.join(self.listenedSongs))

def load_userid_from_dir(dir_path):
	userid_set = set()
	file_list = os.listdir(dir_path)
	for filename in file_list:
		filepath = os.path.join(dir_path,filename)
		with open(filepath,'r') as fin:
			for line in fin.readlines():
				line = line.strip().split('\t')
				userid_set.add(line[0])	
	return userid_set

def main():
	logging.info("Get user's listened song >> begin")
	today = date.today().isoformat()
	today = ''.join(today.split('-'))
	userid_set = load_userid_from_dir('./data/user_info')
	output_path = os.path.join('./data/user_listened','user_listened_'+today)
	tot_num = len(userid_set)
	with open(output_path,'w') as fin:
		for idx,userid in enumerate(userid_set):
			logging.info('Getting listened songs of user:%s\t#%s / %s'%(userid,idx+1,tot_num))
			fin.write(User(userid).data_in_string()+'\n')
	logging.info("Get user's listened song >> complete")

if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/log.user_listened')
	#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	main()
