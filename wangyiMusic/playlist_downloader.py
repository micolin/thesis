#coding=utf8
import urllib2
from lxml import etree
import logging
import os,sys

logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(funcName)s %(lineno)d %(message)s',filename='./log/log.crawl_playlist')

def get_page(url):
	'''
	@params[in] url 
	@return[out] page
	'''
	retry = 5
	page = ''
	while retry > 0:
		try:
			page = urllib2.urlopen(url,timeout=5).read()
			break
		except:
			retry -= 1
			logging.info('Get page:%s failed, retry.'%(url))

	return page

def get_cate_list(filepath):
	'''
	@func: get category info from file
	@params[in] filepath: path of category info
	@return[out] cate_type: dict {cate: c_type}
	'''
	cate_type = {}
	with open(filepath,'rb') as fin:
		for line in fin.readlines():
			line = line.strip().split('\t')
			cate = line[0]
			c_type = line[1]
			cate_type[cate] = c_type
	return cate_type

playlist_url_template = "http://music.163.com/discover/playlist/?cat=%s&limit=35&offset=%s"

def playlist_page_parser(html):
	'''
	@func: parser of playlist page
	@params[in] html: raw html text
	@return[out] playlist_dict: {href: playlist_name}
	@return[out] has_next_page: bool, whether there's next page 
	'''
	dom = etree.HTML(html.decode('utf8'))
	playlists_dom = dom.xpath(u"//ul[@class='m-cvrlst f-cb']")[0]
	playlist_dict = {}
	for playlist in playlists_dom.iterchildren():
		des_doms = playlist.xpath(u"//a[@class='tit f-thide s-fc0']")
		for des_dom in des_doms:
			playlist_name = des_dom.attrib['title']
			playlist_href = des_dom.attrib['href']
			playlist_dict[playlist_href]=playlist_name.encode('utf8')
	
	has_next_page = False
	page_dom = dom.xpath(u"//div[@class='u-page']")
	if page_dom:
		next_page_btn = page_dom[0].xpath(u"//a[@class='zbtn znxt']")
		if next_page_btn:
			has_next_page = True
	return playlist_dict,has_next_page
			
def playlist_crawler(cate_list_path,output_file):
	'''
	@func: main crawl function of playlist spider
	@params[in] cate_list_path: path of category info file
	@params[in] output_file: path of output
	'''
	logging.info("Playlist crawling >>> begin")

	#Get category info
	cate_type = get_cate_list(cate_list_path)
	
	all_playlist = {}
	for (cate,c_type) in cate_type.items():
		logging.info('Parsing cate:%s'%(cate))
		#Transfrom special character to specific form
		n_cate = cate.replace(' ','%20')
		n_cate = n_cate.replace('/','%2F')
		n_cate = n_cate.replace('&','%26')
		has_next_page = True
		offset = 0
		while has_next_page:
			#Combine url
			cate_list_url = playlist_url_template%(n_cate,offset)
			logging.info('Getting playlist page, url: %s'%(cate_list_url))
			playlist_page = get_page(cate_list_url)
			playlists,has_next_page = playlist_page_parser(playlist_page)
			all_playlist.update(playlists)
			if has_next_page:
				offset += 35
	#Output to file
	output_playlists(output_file,all_playlist)
	logging.info("Playlist crawling >>> complete")

def output_playlists(outfile,data):
	'''
	@func: output data to file
	@params[in] outfile: path of output
	@params[in] data: dict,{href,playlist_name}
	'''
	logging.info('Output playlist to file:%s'%(outfile))
	with open(outfile,'w') as fin:
		for (href,playlist_name) in data.items():
			playlist_id = href[href.index('=')+1:]
			fin.write("%s\t%s\t%s\n"%(playlist_id,href,playlist_name))

if __name__=="__main__":
	args = sys.argv
	cate_list_file = args[1]
	output_file = args[2]
	playlist_crawler(cate_list_file,output_file)
