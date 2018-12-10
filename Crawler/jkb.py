# coding: utf-8
"""
Created on ****-**-**
@author: YangLei
@brief: 健康报
@version: Anaconda Python 3.6
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
	pageurl_list = ['http://www.jkb.com.cn/xunyiwenyao/diabetes/',
	            'http://www.jkb.com.cn/xunyiwenyao/hypertension/',
				'http://www.jkb.com.cn/xunyiwenyao/cardiovascular/',
				'http://www.jkb.com.cn/xunyiwenyao/andrology/',
				'http://www.jkb.com.cn/xunyiwenyao/gynecology/',
				'http://www.jkb.com.cn/xunyiwenyao/pediatrics/',
				'http://www.jkb.com.cn/xunyiwenyao/ENT/',
				'http://www.jkb.com.cn/xunyiwenyao/dermatology/',
				'http://www.jkb.com.cn/xunyiwenyao/socialDisease/',
				'http://www.jkb.com.cn/xunyiwenyao/dentistry/',
				'http://www.jkb.com.cn/xunyiwenyao/psychiatric/',
				'http://www.jkb.com.cn/xunyiwenyao/allergicDiseases/',
				'http://www.jkb.com.cn/healthyLiving/gender/',
				'http://www.jkb.com.cn/healthyLiving/mentalHealth/',
				'http://www.jkb.com.cn/healthyLiving/slim/',
				'http://www.jkb.com.cn/healthyLiving/nutrition/',
				'http://www.jkb.com.cn/healthyLiving/cosmeticSurgery/',
				'http://www.jkb.com.cn/healthyLiving/health/',
				'http://www.jkb.com.cn/healthyLiving/parenting/',
				'http://www.jkb.com.cn/healthyLiving/rehabilitation/',
				'http://www.jkb.com.cn/healthyLiving/jkzs/']
	return pageurl_list

def getarturl(pageurl_list, proxy, driver):
	arturl_list = []
	for url in pageurl_list:
		try:
			driver.get(url)
			content = BeautifulSoup(driver.page_source, "lxml")
			results = content.find_all(class_="no-pic")[:10]
			for result in results:
				arturl = result.h4.a["href"]
				art_time = "-".join(re.findall(r'(\d{4})/(\d{2})(\d{2})/',str(arturl))[0])
				art_time = datetime.datetime.strptime(art_time, '%Y-%m-%d').date()
				if art_time >= (datetime.datetime.now() + datetime.timedelta(days=-1)).date():
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
			content = BeautifulSoup(driver.page_source, "lxml").find_all(class_=re.compile("mainL\sfl"))[0]
			title = content.find_all(class_="title")[0].h3.get_text()
			create_date = "-".join(re.findall(r'(\d{4})/(\d{2})(\d{2})/', url)[0])
			create_date = datetime.datetime.strptime(create_date, '%Y-%m-%d').date()
			html = content.find(class_='content')
			htmls=DescArt(html)
			context = htmls.get_text()
			tags = get_tags(title, context)
			channelId = get_channel(title, context)
			categoryId = get_category(channelId, tags)
			print("爬取文章{}".format(title))
			if isSame(title + context) is not False:
				print("正在存储健康报网“{0}”文章".format(title))
				pool.insert_one(
				"insert into article_classify.article_crawler(title,content,tags,channelId,categoryId,create_date) values (%s,%s,%s,%s,%s,%s)",
				(title, str(htmls), tags, channelId, categoryId, create_date))
		except:
			print("格式不一致")


def jkb_craw(proxy, driver):
	pageurl_list = getpageurl()
	arturl_list = getarturl(pageurl_list, proxy, driver)
	get_article(arturl_list, proxy, driver)


if __name__ == "__main__":
	get_proxy = GetProxy()
	option = webdriver.ChromeOptions()
	option.add_argument("headless")
	driver = webdriver.Chrome(chrome_options=option)
	proxy = get_proxy.get_proxy()
	jkb_craw(proxy, driver)
