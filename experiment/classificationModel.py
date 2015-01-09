#coding=utf8
import os,sys
import json, logging
from collections import *
from models import BaseModel, BaseDataSet
from userLDA import UserLDA
from item_tag_CF import ItemTagCF

class ClassificationModel(
