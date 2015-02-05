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
		return render_to_response("test.html")
		
	def build_tag_list(tag_list):
		tag_distrib = []
		for item in tag_list:
			tag_distrib.append(Tag(item[0],item[1]))
		return tag_distrib

	tag_distrib = build_tag_list(json.loads(user.tag_distrib))
	rec_songs = user.rec_songs
	return render_to_response("detail.html",{'rec_songs':rec_songs,'interest':tag_distrib})

def saveUser(request):
	tag_distrib = [('Pop','30%'),('R&B','30%'),('Blue','20%'),('Rock','10%')]
	rec_songs = '2001320,26569168,5138277'
	s_user=User(uid='12341234',user_name='user2',tag_distrib=json.dumps(tag_distrib),rec_songs=rec_songs)
	s_user.save()
	return render_to_response("test.html")
