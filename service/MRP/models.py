from mongoengine import *
connect('mrp_1k',host='172.18.217.101',port=27017)

class User(Document):
	uid = StringField(required=True,primary_key=True)
	user_name = StringField(max_length=100)
	tag_distrib = StringField()

class Song(Document):
	sid = StringField(required=True,primary_key=True)
	song_name = StringField(max_length=100)
	tag_distrib = StringField()

