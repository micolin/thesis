#coding=utf8
import os,sys
from collections import *
import time
from storage import db_connection
import urllib2
from lxml import etree
import logging,json

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/build_it_distrib.log',filemode='w')

def build_ITDistribution_withWeight(item_tag_file):
	'''
	@Desc: build item-tag distribution from database
	@params[in]: item_tag_file: path of output
	'''
	song_tag_distrib=defaultdict(dict)
	#Build item-tag distribution
	time_st = time.time()
	db = db_connection()
	collection = db['playlist_info']
	records = collection.find()
	
	count = 0
	all_times = 0
	for record in records:
		play_times = int(record['play_times'])
		all_times += play_times
		count += 1

	average_playtimes = all_times/count
	records = collection.find()
	for record in records:
		songs = record['songs'].split(',')
		tags = record['tags'].encode('utf8')
		play_times = int(record['play_times'])
		weight = float(play_times)/average_playtimes
		if tags == "none" or weight <=0:
			continue
		for song in songs:
			for tag in tags.split(','):
				try:
					song_tag_distrib[song][tag] += weight
				except:
					song_tag_distrib[song][tag] = weight

	#Dump item-tag distribution to file
	logging.info("Dumping item-tag distribution to file:%s"%(item_tag_file))
	with open(item_tag_file,'wb') as fin:
		for sid,tag_dist in song_tag_distrib.items():
			data_in_json = json.dumps(tag_dist)
			fin.write("%s\t%s\n"%(sid,data_in_json))
	logging.info("Dumping process done..")

def build_ITDistribution_with_singer(item_tag_file):
	'''
	@Desc: build item-tag distribution from database
	@params[in]: item_tag_file: path of output
	'''
	song_tag_distrib=defaultdict(dict)
	#Build item-tag distribution
	time_st = time.time()
	db = db_connection()
	collection = db['playlist_info']
	records = collection.find()

	for record in records:
		songs = record['songs'].split(',')
		tags = record['tags'].encode('utf8')
		if tags == "none":
			continue
		for song in songs:
			for tag in tags.split(','):
				try:
					song_tag_distrib[song][tag] += 1
				except:
					song_tag_distrib[song][tag] = 1

	#Add atrist info into item-tag file
	db = db_connection()
	collection = db['song_info']
	count = 0
	fin = open(item_tag_file,'wb')
	for songid in song_tag_distrib.keys():
		record = collection.find_one({"_id":songid})
		count+=1
		logging.info("Processing cnt:%s"%(count))
		try:
			song_tag_distrib[songid][record['singer_name'].encode('utf8')]=1
		except:
			logging.info('RecordMiss, songid:%s. Get from page.'%(songid))
			try:
				singer = get_singer_from_page(songid)
				song_tag_distrib[songid][singer] = 1
			except:
				logging.info("Get singer failed.Songid:%s"%(songid))
		tag_dist = song_tag_distrib[songid]
		data_in_json = json.dumps(tag_dist)
		fin.write("%s\t%s\n"%(songid,data_in_json))
	'''
	'''
	time_ed = time.time()
	logging.info('Build item-tag distribution cost:%s'%(time_ed - time_st))

def get_page(url):
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

song_url_template = "http://music.163.com/song?id=%s"
def get_singer_from_page(songid):
	html = get_page(song_url_template%(songid))
	dom = etree.HTML(html.decode('utf8'))
	singer_dom = dom.xpath(u"//a[@class='s-fc7']|//span[@class='s-fc7']")
	singer = singer_dom[0].text.encode('utf8')
	return singer

def test():
	db = db_connection()
	collection = db['song_info']
	song_id = '684231'
	record = collection.find_one({"_id":song_id})
	print record['singer_name'].encode('utf8')

if __name__=="__main__":
	args = sys.argv
	job = args[1]
	item_tag_file = args[2]
	func = globals()[job]
	func(item_tag_file)
