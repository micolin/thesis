#coding=utf8
import urllib2

def get_page_with_ref(url,refer_url,sleepTime=0):
    '''
    @params[in] url: main url
	@params[in] ref_url: referer url for page
    @return[out] page
    '''
    retry = 5
    page = ''
	status = 1
    while retry > 0:
        try:
            opener = urllib2.build_opener()
            opener.addheaders = [('Referer',refer_url),('Connection','keep-alive'),('Content-Type','application/x-www-form-urlencoded')]
            response = opener.open(url)
            page = response.read()
            break
        except Exception,e:
            retry -= 1
            logging.info('Get page:%s failed, retry.'%(url))
            logging.error(e)
			status=0
    return page,status

def get_page(url):
    '''
    @params[in] url 
    @return[out] page
    '''
    retry = 5
    page = ''
	status = 1
    while retry > 0:
        try:
            page = urllib2.urlopen(url,timeout=5).read()
            break
        except:
            retry -= 1
            logging.info('Get page:%s failed, retry.'%(url))
			status=0

    return page,status

