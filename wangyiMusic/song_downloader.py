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
		dom = etree.HTML(html)
		self.html = html
		self.song_name,self.singer_id,self.singer_name,self.album_id,self.album_name = self.__get_basic_info(dom)
		self.song_lrc = self.__get_lrc(dom)
		self.sim_songs = self.__get_sim_song(dom)

	def __get_basic_info(self,dom_tree):
		name_dom = dom_tree.xpath(u"//em[@class='f-ff2']")[0]
		song_name = name_dom.text.encode('utf8')
		
		singer_dom = dom_tree.xpath(u"//a[@class='s-fc7']|//span[@class='s-fc7']")
		singer_id = 'none'
		try:
			singer_href = singer_dom[0].attrib['href']
			singer_id = singer_href[singer_href.index('=')+1:]
		except:
			logging.info("There's no id for singer")

		singer_name = singer_dom[0].text.encode('utf8')
		
		album_id = 'none'
		try:
			album_href = singer_dom[1].attrib['href']
			album_id = album_href[album_href.index('=')+1:]
		except:
			logging.info("There's no id for album")
		album_name = singer_dom[1].text.encode('utf8')
		return song_name,singer_id,singer_name,album_id,album_name

	def __get_lrc(self,dom_tree):
		song_lrc = ''
		try:
			lrc_dom = dom_tree.xpath(u"//div[@class='bd bd-open f-brk f-ib']")[0]
			for lrc in lrc_dom.itertext():
				song_lrc += lrc.strip().encode('utf8')
		except:
			logging.info("There's no lrc for song:%s"%(self.song_id))
		
		if "暂时没有歌词" in song_lrc:
			song_lrc = 'none'

		return song_lrc

	def __get_sim_song(self,dom_tree):
		song_list = []
		sim_song_dom = dom_tree.xpath(u"//a[@class='s-fc1']")
		for sim_song in sim_song_dom:
			song_list.append(sim_song.attrib['data-res-id'])
		return song_list

	def data_in_string(self):
		return "%s\t"*8%(self.song_id,self.song_name,self.singer_id,self.singer_name,self.album_id,self.album_name,self.song_lrc,','.join(self.sim_songs))

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

def get_all_song(playlist_info_file):
	logging.info("Song info crawling process >> begin")
	playlist_songs = get_playlists(playlist_info_file)
	for (playlist_id,song_list) in playlist_songs.items():
		for song_id in song_list:
			song_url = song_url_template%(song_id)
			logging.info('Crawl song page of song:%s url:%s'%(song_id,song_url))
			try:
				song_page = get_page(song_url)
				if song_page :
					try:
						song = Song(song_id,song_page)
						print song.data_in_string()
					except Exception,e:
						logging.error('Parsing song page:%s failed...'%(song_url))
				else:
					logging.error("Get song page failed...")
			except Exception, e:
				logging.error("Crawl song page %s Failed"%(song_id))
		break
	logging.info("Song info crawling process >> complete")

if __name__=="__main__":
	args = sys.argv
	playlist_info_file = args[1]
	get_all_song(playlist_info_file)
