#coding=utf8
import urllib2
import os,sys
from collections import *
from lxml import etree
import logging

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/log.crawl_content')

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

wangyi_url_template="http://music.163.com%s"

class Playlist:
	def __init__(self,html):
		self.html = html
		dom = etree.HTML(html.decode('utf8'))
		self.favor_num, self.share_num, self.comment_num = self._get_playlist_info(dom)
		self.play_times = self._get_play_times(dom)
		self.tags, self.desc = self._get_tags_desc(dom)
		self.song_num, self.song_list = self._get_song_list(dom)

	def _get_playlist_info(self,dom_tree):
		favor_num = 0
		share_num = 0
		comment_num = 0
		info_div = dom_tree.xpath(u"//div[@class='btns f-cb j-action']")[0]
		for sub_ele in info_div.iterchildren():
			a_type = sub_ele.attrib['class'].split()[-1]
			if a_type == 'j-fav':
				fav = sub_ele.getchildren()[0].text.encode('utf8')
				favor_num = int(fav[fav.index('(')+1:-1])
			elif a_type == 'j-shr':
				share =  sub_ele.getchildren()[0].text.encode('utf8')
				share_num = int(share[share.index('(')+1:-1])
			elif a_type == 'j-cmt':
				comment = sub_ele.getchildren()[0].text.encode('utf8')
				comment_num = int(comment[comment.index('(')+1:-1])
		return favor_num, share_num, comment_num

	def _get_play_times(self,dom_tree):
		play_times = 0
		return play_times
	
	def _get_tags_desc(self,dom_tree):
		tags = []
		desc = ''
		return tags, desc

	def _get_song_list(self,dom_tree):
		song_num=0
		song_list = {}
		return song_num,song_list
		

def get_playlist_id(filepath):
	with open(filepath,'rb') as fin:
		for idx,line in enumerate(fin.readlines()):
			line = line.strip().split('\t')
			href = line[1]
			playlist_url = wangyi_url_template%(href)
			playlist_page = get_page(playlist_url)
			playlist = Playlist(playlist_page)
			if idx>10:
				break

if __name__=="__main__":
	args = sys.argv
	playlist_file_path=args[1]
	get_playlist_id(playlist_file_path)
