#coidng=utf8
import os,sys
import logging
import random
from storage import db_connection

def select_uid_reservoir(filepath,max_num,database=None):
	'''
	@desc: select userid for training and testing with reservoir simpling
	@params[in] filepath : path of idfile
	@params[in] max_num : limitation of selection
	@return[out]
	'''
	selected_uid = []
	with open(filepath,'r') as fin:
		for idx,line in enumerate(fin.readlines()):
			uid = line.strip()
			favor_songs = get_favorSong_with_id(uid,database)
			#Remove user who has no favor songs
			if favor_songs == None or len(favor_songs) < 10:
				continue
			#Simpling
			if len(selected_uid) < max_num:
				selected_uid.append((uid,favor_songs))
			else:
				rand = random.randint(0,idx)
				if rand < max_num:
					selected_uid[rand]=(uid,favor_songs)
	return selected_uid

def get_favorSong_with_id(userid,database=None,table_name='user_favor_20141215'):
	'''
	@desc: get user's favor songs from database
	@params[in] userid
	@params[in] database: pymongo.db
	@params[in] table_name: name of collection
	'''
	#Connect to db
	db = database
	if db==None:
		db = db_connection()
	#Select collection
	collection = db[table_name]
	#Get record from collection
	record = collection.find_one({'_id':userid})
	favorSongs = record['favor_songs']
	if not favorSongs == None:
		favorSongs = favorSongs.split(',')
	return favorSongs

def build_dataset(filepath,max_num):
	'''
	@Desc: randomly select max_num of user for training and testing
	@params[in] filepath: path of file include all user_id
	@params[in] max_num: int, amount of selected users
	'''
	logging.info("Dataset building process >> Begin")
	db = db_connection()
	uid_list = select_uid_reservoir(filepath,max_num,db)
	for uid,favor_songs in uid_list:
		print "%s\t%s"%(uid,','.join(favor_songs))
	logging.info("Dataset building process >> Complete")

def split_dataset(filepath,train_prob=0.7):
	'''
	@Desc: split dataset into 2 parts: training-set and testing-set
	@params[in] filepath: path of input file, with uid \t favor-songs
	@params[in] train_prob
	'''
	logging.info("Dataset spliting process >> Begin")
	train_list = {}
	test_list = {}
	with open(filepath,'rb') as fin:
		for idx,line in enumerate(fin.readlines()):
			line = line.strip().split('\t')
			uid = line[0]
			favor_songs = line[1].split(',')
			sp_idx = int(train_prob*len(favor_songs))
			_train = favor_songs[:sp_idx]
			_test = favor_songs[sp_idx:]
			train_list[uid] = _train
			test_list[uid] = _test
	
	#Dumping training data and testing data
	logging.info("Dumping training data and testing data to file")
	train_data_output = os.path.join(os.path.dirname(filepath),os.path.basename(filepath)+'_train_'+str(train_prob))
	test_data_output = os.path.join(os.path.dirname(filepath),os.path.basename(filepath)+'_test_'+str(train_prob))
	with open(train_data_output,'w') as fin:
		for uid,data in train_list.items():
			fin.write("%s\t%s\n"%(uid,','.join(data)))
	with open(test_data_output,'w') as fin:
		for uid,data in test_list.items():
			fin.write("%s\t%s\n"%(uid,','.join(data)))

	logging.info("Dataset spliting process >> Complete")

def main():
	args = sys.argv
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	job = args[1]
	inputdir = args[2]
	logging.info("Job name: %s"%(job))
	logging.info("Input Dir: %s"%(inputdir))
	if job == 'build_dataset':
		max_num=int(args[3])
		logging.info("Max Num: %s"%(max_num))
		globals()[job](inputdir,max_num)
	elif job == 'split_dataset':
		train_prob = float(args[3])
		logging.info("Training prop: %s"%(train_prob))
		globals()[job](inputdir,train_prob)
	

if __name__=="__main__":
	main()
