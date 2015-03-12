#coding=utf8
from django.http import *
from django.template.loader import get_template
from django.template import Context, Template, RequestContext
from django.shortcuts import render_to_response
import json
from models import *
from objects import *

def home(request):
	return render_to_response("home.html")

def about(request):
	return render_to_response("about.html")

def search(request):
	return render_to_response("search.html")

def detail(request):
	userid = request.GET['uid']
	try:
		user = User.objects.get(uid=userid)
	except:
		u_crawler = Crawler(userid)
		infos = u_crawler.get_basic_info()
		songs = u_crawler.get_favor_songs()
		print infos
		print songs
		return render_to_response("test.html")
		
	def build_tag_list(tag_list):
		tag_distrib = []
		for item in tag_list:
			tag_distrib.append(Tag(item[0],item[1]))
		return tag_distrib

	tag_distrib = build_tag_list(json.loads(user.tag_distrib))
	rec_songs = user.rec_songs
	return render_to_response("detail.html",{'rec_songs':rec_songs,'interest':tag_distrib})

def ldatopic(request):
	#song_list = '540968,26418808,26447698,825646,28018269,28018274,26341140,29005974,725619,705376' #日语
	#song_list = '27511866,27514438,26145359,27514439,28768734,26562615,28768727,22735484,28768728,28768736' #韩语
	#song_list = '5276808,5276807,5276811,4330195,5276791,127777,5276810,5276804,5276799,28226052'	#交响乐
	#song_list = '1462982,4377220,27406244,3935239,28283167,2070502,27570917,2529459,2061739,1984625'	#史诗级配乐
	#song_list = '28864241,28864234,28864240,28864239,28864235,28864243,28864238,28864245,28864236,28864242'	#电影插曲
	#song_list = '29592140,381838,27731261,18095081,28254854,28547429,27731258,26494849,28860654,381912'	#民谣
	#song_list = '26427653,26145725,27770955,26427665,26427667,26427660,28381284,29328045,28465466,28068703' #民谣+好妹妹
	
	#song_list = '19292800,19292804,27867696,19293014,19292987,19293023,25787222,26221035,19292812,2002351'	#Talyor Swift
	#song_list = '65592,65337,65766,65334,67381,65952,65053,64892,66841' #陈奕迅
	song_list = '28747428,28876107,28876114,28747425,28737747,28747430,28747426,28876112,28876116,28876113'
	#song_list = '155894,155908,155910,155899,155913,155966,25638240,155887,155897,155984'	#汪峰
	#song_list = '385944,386175,385556,385818,386538,385821,385554,385544,385891,25794008'	#五月天
	#song_list = '209478,209314,209216,209235,209112,209129,209268,209028,209115,209238'	#陈绮贞
	return render_to_response("topic.html",{'song_list':song_list})

def saveUser(request):
	tag_distrib = [('Pop','30%'),('R&B','30%'),('Blue','20%'),('Rock','10%')]
	rec_songs = '2001320,26569168,5138277'
	s_user=User(uid='12341234',user_name='user2',tag_distrib=json.dumps(tag_distrib),rec_songs=rec_songs)
	s_user.save()
	return render_to_response("test.html")
