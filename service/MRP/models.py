from mongoengine import *
connect('mrp',host='172.18.217.101',port=27017)

class User(Document):
	uid = StringField(required=True,primary_key=True)
	user_name = StringField(max_length=100)
	area = StringField()
	gender = StringField()
	expertTag = StringField()
	desc = StringField()
	img = StringField()

class Recommend(Document):
	uid = StringField(required=True,primary_key=True)
	interests = StringField()
	rec_songs = StringField()

class Song(Document):
	sid = StringField(required=True,primary_key=True)
	song_name = StringField(max_length=100)
	tag_distrib = StringField()

