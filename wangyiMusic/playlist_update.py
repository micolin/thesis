#coding=utf8
def update(ori_playlist_file, playlist_info):
	ori_playlist = {}
	with open(ori_playlist_file,'rb') as fin:
		for line in fin.readlines():
			line = line.strip().split('\t')
			playlist_id = line[0]
			playlist_href = line[1]
			playlist_name = line[2]
			ori_playlist[playlist_id]=(playlist_href,playlist_name)
	
	with open(playlist_info,'rb') as fin:
		
