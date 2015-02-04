#coding=utf8
import urllib2
from lxml import etree


class Tag(object):
	def __init__(self,tag,dist):
		self.tag = tag
		self.dist = dist

class Crawler(object):
	def __init__(self,uid):
		self.uid = uid

	def __get_favor_songs(self):
		pass

	def __get_basic_info(self):
		pass

	
