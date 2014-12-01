#coding=utf8
import os
def update(playlist_info_dir):
	playlist_info_files = os.listdir(playlist_info_dir)
	exist_playlist = set()
	new_playlist = set()
	for playlist_file in playlist_info_files:
		playlist_info = os.path.join(playlist_info_dir,playlist_file)
		with open(playlist_info,'rb') as fin:
			for line in fin.readlines():
				line = line.strip().split('\t')	
				ori_playlist = line[0]
				exist_playlist.add(ori_playlist)
				sim_playlists = line[9].split(',')
				new_playlist.update(set(sim_playlists))

	for playlist_id in (new_playlist-exist_playlist):
		playlist_href = "/playlist?id=%s"%(playlist_id)
		print "%s\t%s"%(playlist_id,playlist_href)

update('./data/playlist_basic_info')
