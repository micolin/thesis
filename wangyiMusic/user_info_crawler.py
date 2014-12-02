#coding=utf8
import urllib2
import os,sys
from lxml import etree
import logging
import json

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')

class User:
	def __init__(self,user_id):
		self.user_id = user_id
		self.__get_listenedSong()
		self.__get_follows()
		self.__get_fans()

	def __get_follows(self):
		st_idx = 0
		followers = set()
		while True:
			url_temp = 'http://music.163.com/api/user/getfollows/%s?uid=%s&offset=%s&total=true&limit=150'%(self.user_id,self.user_id,st_idx)
			refer_url = 'http://music.163.com/user/follows?id=%s'%(self.user_id)
			logging.info('Getpage: %s'%(url_temp))
			follows_str = get_page(url_temp,refer_url)
			follows_json = json.loads(follows_str)
			follows_list = follows_json['follow']
			if follows_json['more']:
				st_idx += 150
			else:
				break
			break

	def __get_fans(self):
		st_idx = 0
		fans = set()
		while True:
			url_temp = 'http://music.163.com/api/user/getfolloweds/?userId=%s&offset=%s&total=true&limit=100'%(self.user_id,st_idx)
			refer_url = 'http://music.163.com/user/fans?id=%s'%(self.user_id)
			logging.info('Getpage: %s'%(url_temp))
			fans_str = get_page(url_temp,refer_url)
			fans_json = json.loads(fans_str)
			fans_list = fans_json['followeds']
			if fans_json['more']:
				st_idx += 100
			else:
				break
			break

	def __get_listenedSong(self):
		url_temp = 'http://music.163.com/user/listenedSongs/?id=%s'%(self.user_id)
		refer_url = 'http://music.163.com/user/home?id=%s'%(self.user_id)
		logging.info('Get page: %s'%(url_temp))
		songs_json = get_page(url_temp,refer_url)
		listenedSongs = json.loads(songs_json)['listenedSongs']
		return listenedSongs

	def __get_favor_playlists(self,dom_tree):
		pass

def get_page(url,refer_url):
	'''
	@params[in] url 
	@return[out] page
	'''
	retry = 5
	page = ''
	while retry > 0:
		try:
			opener = urllib2.build_opener()
			opener.addheaders = [('Referer',refer_url),('Connection','keep-alive'),('Content-Type','application/x-www-form-urlencoded')]
			response = opener.open(url)
			page = response.read()
			break
		except Exception,e:
			retry -= 1
			logging.info('Get page:%s failed, retry.'%(url))
			logging.error(e)
	return page

if __name__=='__main__':
	User('13979389')
