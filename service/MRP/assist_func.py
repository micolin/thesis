#coding=utf8
import urllib2
import os,sys
from pymongo import Connection
from models import *
from lxml import etree
import json
import logging

db_host = '172.18.217.101'
db_port = 27017

def db_connection(db_name):
	conn = Connection(db_host,db_port)
	db = conn.easyNetMusic
	return db[db_name]

def get_page_with_ref(url,refer_url,sleepTime=0):
    '''
    @params[in] url: main url
    @params[in] ref_url: referer url for page
    @return[out] page
    '''
    retry = 5
    page = ''
    status = 1
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
            status=0
    return page,status

def get_page(url):
    '''
    @params[in] url 
    @return[out] page
    '''
    retry = 5
    page = ''
    status = 1
    while retry > 0:
        try:
            page = urllib2.urlopen(url,timeout=5).read()
            break
        except:
            retry -= 1
            logging.info('Get page:%s failed, retry.'%(url))
            status=0

    return page,status

def get_info_from_page(uid):
	home_url = 'http://music.163.com/user/home?id=%s'%(uid)
	refer_url = 'http://music.163.com/'
	home_page,status = get_page_with_ref(home_url,refer_url)
	desc = 'none'
	img = 'none'
	if status == 1:
		page_dom = etree.HTML(home_page.decode('utf8'))
		
		#Get img url
		img_dom = page_dom.xpath(u"//dt[@class='f-pr']")[0]
		img = img_dom.getchildren()[0].attrib['src']
		#Get desc
		try:
			desc_dom = page_dom.xpath(u"//div[@class='inf s-fc3 f-brk']")
			desc = desc_dom[0].text.encode('utf8')
		except:
			pass
	return desc,img

def saveUserTest(args):
	tag_distrib = [('Pop','30%'),('R&B','30%'),('Blue','20%'),('Rock','10%')]
	rec_songs = '2001320,26569168,5138277'
	s_user=User(uid='18587140',user_name='男人的实力就是RMB',area='黑龙江省 - 绥化市',gender='male',img='http://p4.music.126.net/IkF8xDCIneKvPjCcuwSBsA==/7708676022811081.jpg?param=200y200')
	s_user.save()
	rec = Recommend(uid='18587140',interests=json.dumps(tag_distrib),rec_songs=rec_songs)
	rec.save()

def saveUserInfo(args):
	dataset=args[0]
	rec_file = '/data/micolin/thesis-git/experiment/rec_result/%s/ubhybird_tag_mix_sim_reorder_plus_0.8_%s_0.7_50'%(dataset,dataset)
	uids = set()
	with open(rec_file,'rb') as fin:
		for line in fin.readlines():
			line = line.strip().split('\t')
			uids.add(line[0])
	collection = db_connection('user_info')

	for uid in uids:
		record = collection.find_one({'_id':uid})
		name = record['name']
		area = record['area']
		gender = record['gender']
		expertTag = record['expertTag']
		desc,img = get_info_from_page(uid)
		user = User(uid=uid,user_name=name,area=area,gender=gender,expertTag=expertTag,desc=desc,img=img)
		user.save()
	
def saveUserRec(args):
	dataset=args[0]
	rec_file = '/data/micolin/thesis-git/experiment/rec_result/%s/ubhybird_tag_mix_sim_reorder_plus_0.8_%s_0.7_50'%(dataset,dataset)
	interest_file = '/data/micolin/thesis-git/experiment/song_dataset/mid_data/user_tag_distribution_%s_0.7.json'%(dataset)
	user_interest = {}
	with open(interest_file,'rb') as fin:
		for line in fin.readlines():
			line = line.strip().split('\t')
			uid=line[0]
			interest = json.loads(line[1])
			user_interest[uid]=interest

	with open(rec_file,'rb') as fin:
		for line in fin.readlines():
			line = line.strip().split('\t')
			uid = line[0]
			rec_songs = json.loads(line[1])[:100]
			interest = user_interest[uid].items()
			user_rec = Recommend(uid=uid,interests=json.dumps(interest),rec_songs=json.dumps(rec_songs))
			user_rec.save()
			
		
if __name__=="__main__":
	logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s')
	args = sys.argv
	func = globals()[args[1]]
	func(args[2:])
