#coding=utf8
import os,sys
import time
from collections import *
from models import BaseModel, BaseDataSet
import numpy as np
import logging

class UserCF(BaseModel):
	def __init__(self):
		BaseModel.__init__(self)
	
	def recommend(self,uids):
		
		pass
