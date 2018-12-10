# coding: utf-8
"""
Created on ****-**-**
@author: YangLei
@brief:环球网
@version: Anaconda Python 
"""
import datetime
import re
from configparser import ConfigParser
from DelRepetition.isSame import isSame
from bs4 import BeautifulSoup
from art_classify.news_tags import get_channel, get_category, get_tags
from selenium import webdriver
from mysql_pool import MySqlPool
from proxy.get_proxy import GetProxy

cfg = ConfigParser()
cfg.read('../config.ini')
pool = MySqlPool(db='yjk_data_etl', host=cfg.get('mysql', 'host'), port=int(cfg.get('mysql', 'port')),
				 user=cfg.get('mysql', 'user'), passwd=cfg.get('mysql', 'password'))


def getpageurl():
	pageurl_list = ['http://health.huanqiu.com/health_promotion',
				'http://health.huanqiu.com/xunyiweny',
				'http://health.huanqiu.com/food_safety',
				'http://health.huanqiu.com/baby',
				'http://health.huanqiu.com/health_news',
				'http://health.huanqiu.com/meirongzhengxing']
	return pageurl_list


def getarturl(pageurl_list, proxy, driver):
	arturl_list = []
	for url in pageurl_list:
		try:
			driver.get(url)
			content = BeautifulSoup(driver.page_source, "lxml")
			results = content.find_all(class_=re.compile(r'item\smasonry-brick'))[:10]
			for result in results:
				art_time = "-".join(re.findall(r'(\d{4})-(\d{2})-(\d{2})', result.h6.get_text())[0])
				art_time = datetime.datetime.strptime(art_time, '%Y-%m-%d').date()
				arturl = result.h3.a["href"]
				if art_time >=(datetime.datetime.now() + datetime.timedelta(days=-1)).date():
					arturl_list.append(arturl)
		except:
			print("No page!")
	return arturl_list

def DescArt(html):
	for a in html.find_all("a"):
		a.decompose()
	for img in html.find_all("img"):
		img.decompose()
	for p in html.find_all("p"):
		if "推荐阅读" in p.get_text():
			p.decompose()
	return html

def get_article(arturl_list, proxy, driver):
	for url in arturl_list:
		try:
			driver.get(url)
			content = BeautifulSoup(driver.page_source, "lxml").find(class_="l_a")
			page = content.find(class_='page').get_text()
			if page !="":
				continue
			else:
				title =content.find_all(class_='tle')[0].get_text().strip()
				timesoup=content.find_all(class_="la_t_a")[0].get_text()
				create_date = datetime.datetime.strptime(timesoup, '%Y-%m-%d %H:%M').date()
				html = content.find(class_='la_con')
				x=html.find(class_=re.compile(r'ad.*'))
				if x!=None:
					x.decompose()
				[_.extract() for _ in html('script')]
				htmls=DescArt(html)
				context = htmls.get_text()
				tags = get_tags(title, context)
				channelId = get_channel(title, context)
				categoryId = get_category(channelId, tags)
				print("爬取文章{}".format(title))
				if isSame(title + context) is not False:
					print("正在存储环球网“{0}”文章".format(title))
					pool.insert_one("insert into article_classify.article_crawler(title,content,tags,channelId,categoryId,create_date) values (%s,%s,%s,%s,%s,%s)",(title, str(htmls), tags, channelId, categoryId, create_date))
		except:
			print("格式不一致")


def health_huanqiu_craw(proxy, driver):
	pageurl_list = getpageurl()
	arturl_list = getarturl(pageurl_list, proxy, driver)
	get_article(arturl_list, proxy, driver)


if __name__ == "__main__":
	get_proxy = GetProxy()
	option = webdriver.ChromeOptions()
	option.add_argument("headless")
	driver = webdriver.Chrome(chrome_options=option)
	proxy = get_proxy.get_proxy()
	health_huanqiu_craw(proxy, driver)