#coding=utf8
import os,sys
import json, logging
from collections import *
from models import BaseModel, BaseDataSet
from userLDA import UserLDA
from item_tag_CF import ItemTagCF

class ClassificationModel(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
		self.train_X = []
		self.train_Y = []
	
	def build_feature(self,user_songs)
		pass
