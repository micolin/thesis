#coding=utf8
import urllib2
import os,sys
from lxml import etree
import logging
import json
from datetime import date
from user_info_crawler import get_page
from playlist_content import get_page as get_page_normal

class User:
	def __init__(self,user_id):
		self.user_id = user_id
		self.favor_songs = self.__get_favor_songs()

	def __get_favor_songs(self):
		logging.info('Getting favor song of user:%s'%(self.user_id))
		st_idx = 0
		favor_songs = []
		url_temp = 'http://music.163.com/api/user/playlist?uid=%s&wordwrap=7&offset=%s&total=false&limit=%s'%(self.user_id,st_idx,20)
		refer_url = 'http://music.163.com/user/home?id=%s'%(self.user_id)
		playlist_str = get_page(url_temp,refer_url)
		playlist_json = json.loads(playlist_str)
		favor_playlist = playlist_json['playlist'][0]
		pl_id =  favor_playlist['id']

		def get_song_from_playlist(playlist_id):
			playlist_url = 'http://music.163.com/playlist?id=%s'%(playlist_id)
			html = get_page_normal(playlist_url)
			dom_tree = etree.HTML(html)
			#Get songs id
			song_list = []
			songlist_dom = dom_tree.xpath(u"//tbody[@id='m-song-list-module']")[0]
			for song_dom in songlist_dom.getchildren():
				song_list.append(song_dom.attrib['data-id'])
			return song_list

		try:
			favor_songs = get_song_from_playlist(pl_id)
		except Exception,e:
			logging.error('Get favor song of user %s failed. With error:%s'%(self.user_id,e))
		return favor_songs
	
	def data_in_string(self):
		return "%s\t%s"%(self.user_id,','.join(self.favor_songs))

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
	logging.info("Get user's favor songs >> begin")
	today = date.today().isoformat()
	today = ''.join(today.split('-'))
	userid_set = load_userid_from_dir('./data/user_info')
	output_path = os.path.join('./data/user_favor_songs','user_favor_'+today)
	tot_num = len(userid_set)
	with open(output_path,'w') as fin:
		for idx,userid in enumerate(userid_set):
			logging.info('Getting favor songs of user:%s\t#%s / %s'%(userid,idx+1,tot_num))
			fin.write(User(userid).data_in_string()+'\n')
	logging.info("Get user's favor songs >> complete")

if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/log.user_favor_songs')
	#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	main()
