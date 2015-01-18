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
	pass

def testbase(request):
	return render_to_response("base.html")
