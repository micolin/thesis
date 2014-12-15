#coding=utf8
import urllib2
from lxml import etree
import os,sys
import logging
import json
from song_downloader import get_songs_from_idfile
from user_info_crawler import get_page

def get_song_comment(song_id):
	limit = 300
	song_comment_api = 'http://music.163.com/api/resource/comments/R_SO_4_%s/?rid=R_SO_4_%s&offset=%s&total=false&limit=%s'
	song_comments = []
	st_idx = 0
	while True:
		song_comment_url = song_comment_api%(song_id,song_id,st_idx,limit)
		refer_url = 'http://music.163.com/song?id=%s'%(song_id)
		comment_string = get_page(song_comment_url,refer_url)
		comment_json = json.loads(comment_string)
	
		comments = comment_json['comments']
		for comment in comments:
			comm_user = comment['user']['userId']
			replied_user = 'none'
			try:
				replied_user = comment['beRepliedUser']['userId']
			except:
				pass
			comm_content = comment['content'].encode('utf8').strip()
			comm_content = comm_content.replace('\n',';')
			song_comments.append(comm_user,replied_user,comm_content)
		more = comment_json['more']
		if more:
			st_idx+=limit
		else:
			break
	return song_comments

def comment_downloader(filepath):
	logging.info("Song info crawling process >> begin")
	all_songs = get_songs_from_idfile(filepath)
	songs_count = len(all_songs)
	for idx,song_id in enumerate(all_songs):
		logging.info('Crawl comment of song:%s #%s of %s'%(song_id,idx+1,songs_count))
		song_comments = get_song_comment(song_id)
		if idx>10:
			break

if __name__=="__main__":
	args = sys.argv
	file_path = args[1]
	#log_file = args[2]
	#logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='/data/micolin/thesis-git/wangyiMusic/log/'+log_file)
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	#comment_downloader(file_path)
