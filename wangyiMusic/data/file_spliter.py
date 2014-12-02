#coding=utf8
import os,sys
sys.path.append('/data/micolin/thesis-git/wangyiMusic')
from song_downloader import get_songs_from_file

def file_spliter(input_file,num_per_file,output_path):
	songs = get_songs_from_file(input_file)
	id_storage = []
	split_idx = 0
	for idx,song_id in enumerate(songs):
		id_storage.append(song_id+'\n')
		if (idx+1)%num_per_file==0:
			output_file = "%s_%s"%(output_path,split_idx)
			output2file(id_storage,output_file)
			split_idx += 1
			id_storage = []
	
	output_file = "%s_%s"%(output_path,split_idx)
	output2file(id_storage,output_file)

def output2file(data,output_file):
	with open(output_file,'w') as fin:
		for line in data:
			fin.write(line)

if __name__=="__main__":
	args = sys.argv
	input_file = args[1]
	num_per_file = int(args[2])
	output_path = args[3]
	file_spliter(input_file,num_per_file,output_path)
