#coding=utf8
import urllib2
from lxml import etree
import json, logging
from datetime import date
from assist_func import *

class Tag(object):
	def __init__(self,tag,dist):
		self.tag = tag
		self.dist = dist

class Crawler(object):
	def __init__(self,uid):
		self.uid = uid

	def get_favor_songs(self):
		logging.info('Getting favor song of user:%s'%(self.uid))
		st_idx = 0
		favor_songs = []
		url_temp = 'http://music.163.com/api/user/playlist?uid=%s&wordwrap=7&offset=%s&total=false&limit=%s'%(self.uid,st_idx,20)
		refer_url = 'http://music.163.com/user/home?id=%s'%(self.uid)
		playlist_str,status = get_page_with_ref(url_temp,refer_url)
		playlist_json = json.loads(playlist_str)
		favor_playlist = playlist_json['playlist'][0]
		pl_id =  favor_playlist['id']

		def get_song_from_playlist(playlist_id):
			playlist_url = 'http://music.163.com/playlist?id=%s'%(playlist_id)
			html,status = get_page(playlist_url)
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
			logging.error('Get favor song of user %s failed. With error:%s'%(self.uid,e))
		return favor_songs

	def get_basic_info(self):
		logging.info("Getting basic info of user:%s"%(self.uid))
		home_url = 'http://music.163.com/user/home?id=%s'%(self.uid)
		refer_url = 'http://music.163.com/'
		home_page,status = get_page_with_ref(home_url,refer_url)
		page_dom = etree.HTML(home_page.decode('utf8'))
		
		#Get user's name
		name_dom = page_dom.xpath(u"//span[@class='tit f-ff2 s-fc0']")[0]
		user_name = name_dom.text.encode('utf8')

		#Get user's area 
		user_area = 'none'
		try:
			area_dom = page_dom.xpath(u"//div[@class='inf s-fc3']")[0]
			user_area = area_dom.getchildren()[0].text.encode('utf8')
			user_area = user_area[user_area.index('：')+3:]
		except Exception,e:
			logging.info("There's no area info for user:%s"%(self.uid))
		
		#Get user's gender
		user_gender = 'none'
		try:
			male_dom = page_dom.xpath(u"//i[@class='icn u-icn u-icn-01']")
			female_dom = page_dom.xpath(u"//i[@class='icn u-icn u-icn-02']")
			if len(male_dom) and not len(female_dom):
				user_gender = 'male'
			elif len(female_dom) and not len(male_dom):
				user_gender = 'female'
		except:
			pass

		#Get expertsTag
		tags = 'none'
		try:
			tag_dom = page_dom.xpath(u"//p[@class='djp f-fs1 s-fc3']")[0]
			user_tag = ''
			for text in tag_dom.itertext():
				user_tag += text.strip().encode('utf8')
			user_tag = user_tag[:user_tag.index("领域达人")].split('，')
			tags = ','.join(user_tag)
		except Exception,e:
			logging.info("There's no expertsTag info for user:%s"%(self.uid))
			
		return user_name,user_gender,user_area,tags

class MUser(object):
	def __init__(self,uid):
		self.uid = uid

	def cal_user_tag_distrib(self):
		pass

	def cal_user_sim_with_tag(self):
		pass
