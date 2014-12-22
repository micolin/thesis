#coding=utf8
import config
from pymongo import Connection
import logging

def db_connection():
	'''
	@desc: get mongodb connection
	@return[out] object of db connection
	'''
	logging.info('Connect to database @%s:%s'%(config.db_host,config.db_port))
	conn = Connection(config.db_host,config.db_port)
	db = conn.easyNetMusic
	return db
