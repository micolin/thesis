#coding=utf8
import urllib2
import os,sys
from collections import *
from lxml import etree
import logging
from storage import connect_to_db

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
	def __init__(self,playlist_id,html):
		self.html = html
		self.playlist_id = playlist_id
		dom = etree.HTML(html.decode('utf8'))
		self.playlist_name = self.__get_playlist_name(dom)
		self.creator = self.__get_creator(dom)
		self.favor_num, self.share_num, self.comment_num = self.__get_playlist_info(dom)
		self.play_times = self.__get_play_times(dom)
		self.tags, self.desc = self.__get_tags_desc(dom)
		self.sim_playlists = self.__get_sim_playlist(dom)
		self.song_num, self.song_list = self.__get_song_list(dom)

	def __get_playlist_name(self,dom_tree):
		playlist_name=''
		try:
			name_dom = dom_tree.xpath(u"//h2[@class='f-ff2 f-brk']")[0]
			playlist_name = name_dom.text.encode('utf8')
		except Exception, e:
			loggin.error('Parsing playlist_name error...')
			logging.error(e)
		return playlist_name

	def __get_creator(self,dom_tree):
		creator = ''
		try:
			creator_dom = dom_tree.xpath(u"//a[@class='s-fc7']")[0]
			creator = creator_dom.attrib['href']
			creator = creator[creator.index('=')+1:]
		except Exception, e:
			logging.error('Parsing creator error...')
			logging.error(e)
		return creator

	def __get_playlist_info(self,dom_tree):
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

	def __get_play_times(self,dom_tree):
		play_times = 0
		try:
			times_dom = dom_tree.xpath(u"//strong[@class='s-fc6 j-play-count']")[0]
			play_times = int(times_dom.text)
		except Exception,e:
			logging.error('Parse play times error..')
			logging.error(e)
		return play_times
	
	def __get_tags_desc(self,dom_tree):
		tags = []
		desc = ''
		try:
			tags_dom = dom_tree.xpath(u"//div[@class='tags f-cb']")[0]
			for child in tags_dom.getchildren():
				if child.tag == 'a':
					tag = child.getchildren()[0].text.encode('utf8')
					tags.append(tag)
		except Exception,e:
			logging.info("There's no tags for playlist")
			logging.error(e)
			
		try:
			desc_dom = dom_tree.xpath(u"//p[@class='intr f-brk']")[0]
			for text in desc_dom.itertext():
				desc += text.encode('utf8')
		except Exception,e:
			logging.info("There's no description for playlist")
			logging.error(e)

		if not desc:
			desc = 'none'

		if len(tags)==0:
			tags = ['none']

		return tags, desc

	def __get_song_list(self,dom_tree):
		song_num=0
		song_list = []
		
		#Get amount of song
		num_dom = dom_tree.xpath(u"//span[@class='sub s-fc3 j-track-count']")[0]
		song_num_text = num_dom.text.encode('utf8')
		song_num = int(song_num_text[:song_num_text.index('首')])
		
		#Get songs id
		songlist_dom = dom_tree.xpath(u"//tbody[@id='m-song-list-module']")[0]
		for song_dom in songlist_dom.getchildren():
			song_list.append(song_dom.attrib['data-id'])
	
		return song_num,song_list

	def __get_sim_playlist(self,dom_tree):
		sim_playlists = []
		try:
			sim_playlist_dom = dom_tree.xpath(u"//a[@class='sname f-fs1 s-fc0']")
			for sub_ele in sim_playlist_dom:
				sim_playlists.append(sub_ele.attrib['data-res-id'])
		except Exception,e:
			logging.error('Get sim_playlist id error, pass')
			logging.error(e)

		return sim_playlists
	
	def data_in_string(self):
		return "%s\t"*12%(self.playlist_id,self.playlist_name,self.creator,self.favor_num,self.share_num,self.comment_num,','.join(self.tags),self.desc,self.play_times,','.join(self.sim_playlists),self.song_num,','.join(self.song_list))

	def storage_to_db(self,db,table_name):
		collection = db[table_name]
		data = {}
		data['_id'] = self.playlist_id
		data['name'] = self.playlist_name
		data['creator'] = self.creator
		data['favor_num'] = self.favor_num
		data['share_num'] = self.share_num
		data['comment_num'] = self.comment_num
		data['tags'] = ','.join(self.tags)
		data['desc'] = self.desc
		data['play_times'] = self.play_times
		data['sim_playlists'] = ','.join(self.sim_playlists)
		data['songs'] = ','.join(self.song_list)
		collection.insert(data)

def crawl_playlist_info(filepath):
	'''
	@func: main process of playlist spider
	@params[in] filepath: path of playlist_dict 
	'''
	logging.info('Crawl playlist info from web >> begin')
	db = connect_to_db()
	table_name = 'playlist_info'
	with open(filepath,'rb') as fin:
		for idx,line in enumerate(fin.readlines()):
			line = line.strip().split('\t')
			href = line[1]
			playlist_id = line[0]

			#Combine url
			playlist_url = wangyi_url_template%(href)
			logging.info("Crawling playlist: %s #%s"%(playlist_url,idx))
			try:
				playlist_page = get_page(playlist_url)
				if playlist_page :
					try:
						playlist = Playlist(playlist_id,playlist_page)
						playlist.storage_to_db(db,table_name)
					except Exception, e:
						logging.error('Parsing playlist: %s failed..'%(playlist_url))
						logging.error(e)
				else:
					logging.error("Get playlist page failed...")
			except Exception,e:
				logging.error("Crawl playlist: %s filed..."%(playlist_id))
				logging.error(e)
	logging.info('Crawl playlist info from web >> complete')

if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/log.crawl_content',filemode='w')
	#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	args = sys.argv
	playlist_file_path=args[1]
	crawl_playlist_info(playlist_file_path)
