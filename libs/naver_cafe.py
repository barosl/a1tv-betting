import urllib2, cookielib
import re

def sign_in(username, password):
	cj = cookielib.CookieJar()
	opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

	opener.open('https://nid.naver.com/nidlogin.login', data='id=%s&pw=%s' % (username, password))

	return opener

def get_articles_from_page(opener, page):
	articles = []

	url = 'http://cafe.naver.com/ArticleList.nhn?search.boardtype=L&search.menuid=424&search.questionTab=A&search.clubid=18863363&search.totalCount=28&search.page=%d' % page
	fp = opener.open(url)
	data = fp.read()
	rows = re.findall('a href=\'(/ArticleRead.nhn[^\']+)\'[^>]*>([^<]*)</a>(?:\\s*<input type="text" class="list-i-([^"]+))?', data)
	for row in rows:
		url, name, atype = row

		url = 'http://cafe.naver.com/'+url.replace('&amp;', '&')
		name = name.decode('cp949', 'replace').encode('utf-8')

		articles.append({'url': url, 'name': name, 'type': atype})

	return articles

def get_articles(opener):
	articles = []
	page = 1
	while True:
		cur_articles = get_articles_from_page(opener, page)
		if not cur_articles: break
		articles += cur_articles
		page += 1
	articles.reverse()
	return articles

def get_bettors_from_page(opener, poll_key, item_id, page):
	url = 'http://cafe.poll.naver.com/voterDisplay.nhn?pollKey=%s&itemId=%s&page=%d&serviceId=' % (poll_key, item_id, page)
	fp = opener.open(url)
	data = fp.read()
	try: data = re.search('(?s)<colgroup>(.*?)</table>', data).group(1)
	except AttributeError: return []
	bettors = re.findall('<td>([^<]+)', data)
	return bettors

def get_bettors(opener, poll_key, item_id):
	bettors = []
	page = 1
	while True:
		cur_bettors = get_bettors_from_page(opener, poll_key, item_id, page)
		if not cur_bettors: break
		bettors += cur_bettors
		page += 1
	return bettors
