#coding=utf8
import urllib2
import os,sys
from lxml import etree
from collections import *
import logging

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')

def get_page(url):
	'''
	@params[in] url 
	@return[out] page
	'''
	retry = 5
	page = ''
	while retry > 0:
		try:
			page = urllib2.urlopen(url,timeout=5).read()
			break
		except:
			retry -= 1
			logging.info('Get page:%s failed, retry.'%(url))

	return page

class Song:
	def __init__(self,song_id,html=''):
		self.song_id = song_id
		self.html = html
	
	def __get_basic_info(self):
		pass

	def __get_action_info(self):
		pass

	def __get_lrc(self):
		pass
	
	def __get_sim_song(self):
		pass

def get_playlists(filepath):
	playlist_songs = {}
	with open(filepath,'rb') as fin:
		for line in fin.readlines():
			line = line.strip().split('\t')
			playlist_id = line[0]
			song_list = line[-1].split(',')
			playlist_songs[playlist_id]=song_list
	return playlist_songs

song_url_template = "http://music.163.com/song?id=%s"

def get_all_song():
	playlist_songs = get_playlists('./data/playlist.basic_info')
	for (playlist_id,song_list) in playlist_songs.items():
		for song_id in song_list:
			song_url = song_url_template%(song_id)
			print song_url
		break

if __name__=="__main__":
	get_all_song()
