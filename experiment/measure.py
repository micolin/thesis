#coding=utf8
import sys,os
import json
class Measurer(object):
	def __init__(self):
		self.rec_result = {}
		self.test_set = {}
		self.tot_song = 0

	def score(self,top_n):
		'''
		@Desc: measure precision, recall and f_score of recommendation
		@params[in] test_set: BaseDataSet.test_data, {uid:[songid,]}
		@return[out] score: dict, {precision:pre, recall: rc, f_score: f_s}
		'''
		hit = 0
		predict_tot = 0
		recall_tot = 0
		rec_songs = set()
		for uid, predict_songs in self.rec_result.iteritems():
			predict_songs = predict_songs[:top_n]	#取top_n个推荐
			test_songs = self.test_set[uid]
			hit += len(set(predict_songs) & set(test_songs))
			predict_tot += len(predict_songs)
			recall_tot += len(test_songs)
			rec_songs.update(set(predict_songs))
		
		precision = float(hit)/predict_tot
		recall = float(hit)/recall_tot
		if precision==0 and recall == 0:
			fscore = 0.0
		else:
			fscore = 2.0*(precision*recall)/(precision+recall)

		enrich=float(len(rec_songs))/self.tot_song
		scores = {'precision':precision,'recall':recall,'f_score':fscore,'cover_rate':enrich}
		return scores

	def build_data(self,rec_file,train_file,test_file):
		with open(rec_file,'rb') as fin:
			for line in fin.readlines():
				line = line.strip().split('\t')
				self.rec_result[line[0]] = json.loads(line[1])

		all_songs = set()
		with open(train_file,'rb') as fin:
			for line in fin.readlines():
				line = line.strip().split('\t')
				all_songs.update(set(line[1].split(',')))
			self.tot_song = len(all_songs)

		with open(test_file,'rb') as fin:
			for line in fin.readlines():
				line = line.strip().split('\t')
				self.test_set[line[0]] = [song for song in line[1].split(',') if song in all_songs]

if __name__=="__main__":
	args = sys.argv
	method = args[1]
	dataset = args[2]
	train_prob = args[3]
	user_k = args[4]
	
	#Filepath config
	rec_file = './rec_result/%s_%s_%s_%s'%(method,dataset,train_prob,user_k)
	train_file = './song_dataset/user_dataset_%s_train_%s'%(dataset,train_prob)
	test_file = './song_dataset/user_dataset_%s_test_%s'%(dataset,train_prob)
	measurer = Measurer()
	measurer.build_data(rec_file,train_file,test_file)
	
	for top_n in range(10,101,10):
		score = measurer.score(top_n)
		print top_n,score
	
