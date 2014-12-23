#coding=utf8
import os,sys
import time
from collections import *
from models import BaseModel, BaseDataSet
import logging

class ItemCF(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
	
	def recommend(self,uids,):
		pass
