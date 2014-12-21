#coding=utf8
from collections import *
import os,sys

playlist_info_dir = '/data/micolin/thesis-git/wangyiMusic/data/playlist_basic_info/'
playlist_file = 'playlist.basic_info_all'

def main():
	full_file_path = os.path.join(playlist_info_dir,playlist_file)
	song_tags = defaultdict(list)
	with open(full_file_path,'rb') as fin:
		for line in fin.readlines():
			line = line.strip().split('\t')
			tags = line[6]
			if tags == 'none':
				continue
			tags = tags.split(',')
			songs = line[-1].split(',')
			for songid in songs:
				song_tags[songid] += tags

	for songid,tags in song_tags.items():
		tag_count = defaultdict(int)
		for tag in tags:
			tag_count[tag]+=1
		tag_out = ''
		for tag,count in tag_count.items():
			tag_out += tag+":"+str(count)+'\t'
		print songid+'\t'+tag_out.strip()

if __name__=="__main__":
	main()
