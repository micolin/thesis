from django.http import *
from django.template.loader import get_template
from django.template import Context, Template, RequestContext
from django.shortcuts import render_to_response
from models import *

def homepage(request):
	return render_to_response("homepage.html")

def home(request):
	return render_to_response("home.html")

def about(request):
	return render_to_response("about.html")

def search(request):
	pass

def detail(request):
	rec_songs = '2001320,26569168,5138277'
	return render_to_response("detail.html",{'rec_songs':rec_songs})

