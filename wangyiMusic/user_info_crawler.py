#coding=utf8
import urllib2
import os,sys
from lxml import etree
import logging
import json

class User:
	def __init__(self,user_id):
		self.user_id = user_id
		self.name,self.gender,self.area,self.tags,self.action = self.__get_basic_info()
		self.listenedSongs = self.__get_listenedSong()
		self.follows = self.__get_follows()
		self.fans = self.__get_fans()
		self.collections = self.__get_favor_playlists()
		'''
		print "Uid:%s"%(self.user_id)
		print "Name:%s,Tag:%s,Action:%s"%(self.user_name,self.user_tags,self.user_action)
		print "Follows:",len(self.follows)
		print "Fans:",len(self.fans)
		print "Collections:",len(self.collections)
		'''

	def __get_basic_info(self):
		logging.info("Getting basic info of user:%s"%(self.user_id))
		home_url = 'http://music.163.com/user/home?id=%s'%(self.user_id)
		refer_url = 'http://music.163.com/'
		home_page = get_page(home_url,refer_url)
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
			logging.info("There's no area info for user:%s"%(self.user_id))
		
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
			logging.info("There's no expertsTag info for user:%s"%(self.user_id))
			
		#Get user's action info
		event_num = int(page_dom.xpath(u"//strong[@id='event_count']")[0].text)
		follows_num = int(page_dom.xpath(u"//strong[@id='follow_count']")[0].text)
		fans_num = int(page_dom.xpath(u"//strong[@id='fan_count']")[0].text)
			
		return user_name,user_gender,user_area,tags,(event_num,follows_num,fans_num)

	def __get_follows(self):
		logging.info('Getting follows list of user:%s'%(self.user_id))
		st_idx = 0
		followers = set()
		while True:
			url_temp = 'http://music.163.com/api/user/getfollows/%s?uid=%s&offset=%s&total=true&limit=150'%(self.user_id,self.user_id,st_idx)
			refer_url = 'http://music.163.com/user/follows?id=%s'%(self.user_id)
			follows_str = get_page(url_temp,refer_url)
			follows_json = json.loads(follows_str)
			follows_list = follows_json['follow']
			for follow in follows_list:
				fo_uid = str(follow['userId'])
				event_count = follow['eventCount']	# num of events
				follows_count = follow['follows']		# num of follower
				if event_count > 10 and follows_count>10: 
					followers.add(fo_uid)
			if follows_json['more']:
				st_idx += 150
			else:
				break
		return followers

	def __get_fans(self):
		logging.info('Getting fans list of user:%s'%(self.user_id))
		st_idx = 0
		fans = set()
		while True:
			url_temp = 'http://music.163.com/api/user/getfolloweds/?userId=%s&offset=%s&total=true&limit=100'%(self.user_id,st_idx)
			refer_url = 'http://music.163.com/user/fans?id=%s'%(self.user_id)
			fans_str = get_page(url_temp,refer_url)
			fans_json = json.loads(fans_str)
			fans_list = fans_json['followeds']
			for fan in fans_list:
				f_uid = str(fan['userId'])
				event_c = fan['eventCount']	# num of events
				follows = fan['follows']		# num of follower
				#followeds = fan['followeds']	# num of fan
				#playlist_count = fan['playlistCount']
				if event_c > 10 and follows > 10:
					#print "__Fans:%s, event:%s, follows:%s, followeds:%s"%(f_uid,event_c,follows,followeds)
					fans.add(f_uid)
			if fans_json['more'] and st_idx < 900:
				st_idx += 100
			else:
				break
		return fans

	def __get_listenedSong(self):
		logging.info('Getting listened songs of user:%s'%(self.user_id))
		url_temp = 'http://music.163.com/user/listenedSongs/?id=%s'%(self.user_id)
		refer_url = 'http://music.163.com/user/home?id=%s'%(self.user_id)
		songs_json = get_page(url_temp,refer_url)
		listenedSongs = json.loads(songs_json)['listenedSongs']
		song_list = []
		for song in listenedSongs:
			song_id = str(song['id'])
			song_list.append(song_id)
		return song_list

	def __get_favor_playlists(self):
		logging.info('Getting favor playlist of user:%s'%(self.user_id))
		st_idx = 0
		favor_playlist = []
		while True:
			url_temp = 'http://music.163.com/api/user/playlist?uid=%s&wordwrap=7&offset=%s&total=false&limit=%s'%(self.user_id,st_idx,300)
			refer_url = 'http://music.163.com/user/home?id=%s'%(self.user_id)
			playlist_str = get_page(url_temp,refer_url)
			playlist_json = json.loads(playlist_str)
			playlist_list = playlist_json['playlist']
			for playlist in playlist_list:
				creator = str(playlist['creator']['userId'])
				if not creator == self.user_id:
					favor_playlist.append(str(playlist['id']))
			if playlist_json['more']:
				st_idx += 300
			else:
				break
		return favor_playlist

	def data_with_string(self):
		return "%s\t"*10%(self.user_id,self.name,self.gender,self.area,self.tags,self.action,','.join(list(self.listenedSongs)),','.join(list(self.fans)),','.join(list(self.follows)),','.join(list(self.collections)))

def get_page(url,refer_url,sleepTime=0):
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

def output2file(filepath,data):
	logging.info("Dumping data to file:%s"%(filepath))
	with open(filepath,'w') as fin:
		for user in data:
			fin.write(user.data_with_string()+'\n')

def load_dowloaded_user(filepath):
	logging.info('Loading userid from path:%s.'%(filepath))
	all_userid = set()
	if os.path.isdir(filepath):
		logging.info('%s is dir.'%(filepath))
		path_list = os.listdir(filepath)
		for path in path_list:
			full_path = os.path.join(filepath,path)
			id_set = get_userid(full_path)
			all_userid.update(id_set)
	else:
		logging.info('%s is file.'%(filepath))
		id_set = get_userid(filepath)
		all_userid.update(id_set)
	return all_userid

def get_userid(filepath):
	all_user = set()
	with open(filepath,'r') as fin:
		for line in fin.readlines():
			line = line.strip().split('\t')
			user_id = line[0]
			all_user.add(user_id)
	return all_user

def user_downloader(user_seed,max_user_num,record_per_file,output_dir,existed_user_set=set()):
	'''
	@params[in] user_seed: list,list of user_id as seed
	@params[in]	max_user_num: int,target amount of user
	@params[in] record_per_file: int,amount of user per file
	@params[in] output_dir: path, dir of output
	'''
	logging.info("User infomation crawling >> begin")
	user_bucket = set()		#Store uncaught user_id
	cached_user_set = set()	#Store downloaded user_id
	cached_user_set.update(existed_user_set)
	
	output_file_idx = 0		#Use to split users to different file
	output_data = []		#Cache user objects
	
	total_count = 0			#Total count of downloaded user
	output_filename_temp = 'user_info_%s'
	
	user_bucket.update(set(user_seed))		#Add seed to user bucket
	while user_bucket:
		user_id = user_bucket.pop()
		user = User(user_id)			#Create User object with user_id
		cached_user_set.add(user_id)
		output_data.append(user)
		total_count += 1
		
		#Update user_bucket with user's fans and follows
		user_fans_update = user.fans - cached_user_set
		user_follows_update = user.follows - cached_user_set
		user_bucket.update(user_fans_update)
		user_bucket.update(user_follows_update)
		
		#Dump user's info to file
		if len(output_data) >= record_per_file:
			output_path = os.path.join(output_dir,output_filename_temp%(output_file_idx))
			output_file_idx += 1
			output2file(output_path,output_data)
			output_data = []

		logging.warn("Bucket size:%s"%(len(user_bucket)))
		logging.warn("Current downloaded count:%s"%(total_count))
		if total_count >= max_user_num:
			break

	#Save remain data
	if output_data:
		output_path = os.path.join(output_dir,output_filename_temp%(output_file_idx))
		output2file(output_path,output_data)

	logging.info("User infomation crawling >> complete")

if __name__=='__main__':
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/log.user_downloader')
	#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	user_seed = ['37316751','233041','98971']
	existed_user_set = load_dowloaded_user('./data/user_info/')
	user_downloader(user_seed,100000,10000,'./data/user_info_2nd',existed_user_set)
