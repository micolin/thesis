#coding=utf8
import sys,os
import json
import matplotlib.pyplot as plt
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

def measurement(args):
	method = args[2]
	dataset = args[3]
	train_prob = args[4]
	user_k = args[5]
	top_n = int(args[6])
	
	#Filepath config
	topic_num = 3000
	rec_file = './rec_result/%s/%s_%s_%s_%s'%(dataset,method,dataset,train_prob,user_k)
	if method in ['rs','pop']:
		rec_file = './rec_result/%s_%s_%s'%(method,dataset,train_prob)
	elif method == 'userLDA' or 'lda' in method:
		rec_file = './rec_result/%s/%s_%s_%s_%s_%s'%(dataset,method,dataset,train_prob,topic_num,user_k)
			
	train_file = './song_dataset/user_dataset_%s_train_%s'%(dataset,train_prob)
	test_file = './song_dataset/user_dataset_%s_test_%s'%(dataset,train_prob)
	measurer = Measurer()
	measurer.build_data(rec_file,train_file,test_file)
	
	score = measurer.score(top_n)
	print top_n,score

def plot(args):
	dataset = args[2]
	train_prob = args[3]
	user_k = args[4]
	mea_type = args[5]
	topic_num = int(args[6])
	methods = ['rs','pop','userCF','userLDA','userTagCF','ubhybird_mix_sim_reorder']
	methods = ['rs','pop','userCF','ubhybird_mix_sim_reorder']
	#methods = ['userCF']

	for method in methods:
		if method in ['rs','pop']:
			rec_file = './rec_result/%s_%s_%s'%(method,dataset,train_prob)
		elif 'lda' in method or method == 'userLDA':
			rec_file = './rec_result/%s_%s_%s_%s_%s'%(method,dataset,train_prob,topic_num,user_k)
		else:	
			rec_file = './rec_result/%s_%s_%s_%s'%(method,dataset,train_prob,user_k)
		train_file = './song_dataset/user_dataset_%s_train_%s'%(dataset,train_prob)
		test_file = './song_dataset/user_dataset_%s_test_%s'%(dataset,train_prob)
		measurer = Measurer()
		measurer.build_data(rec_file,train_file,test_file)
		scores = []
		for top_n in range(1,400,1):
			score = measurer.score(top_n)[mea_type]
			scores.append((top_n,score))
		line = plt.plot([score[0] for score in scores],[score[1] for score in scores],linewidth=2, label=method)
	if mea_type in ['recall','cover_rate']:
		plt.legend(loc='upper left')
	else:	
		plt.legend(loc='upper right')
	plt.show()

if __name__=="__main__":
	args = sys.argv
	func = globals()[args[1]]
	func(args)
