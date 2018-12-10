# coding: utf-8
"""
Created on ****-**-**
@author: YangLei
@brief: 健康时报网
@version: Anaconda Python 3.6
"""
import datetime
import re
import time
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
	url_list = ['http://www.jksb.com.cn/html/life/food/',
				'http://www.jksb.com.cn/html/life/chinesemedicine/',
				'http://www.jksb.com.cn/html/life/nvxing/',
				'http://www.jksb.com.cn/html/life/baby/',
				'http://www.jksb.com.cn/html/life/sex/',
				'http://www.jksb.com.cn/index.php?m=content&c=index&a=list_posids&posid=217&page=1',
				'http://www.jksb.com.cn/index.php?m=content&c=index&a=list_posids&posid=218&page=1',
				'http://www.jksb.com.cn/index.php?m=content&c=index&a=list_posids&posid=215&page=1',]
	return url_list

def DescArt(html):
	for a in html.find_all("a"):
		a.decompose()
	for img in html.find_all("img"):
		img.decompose()
	for p in html.find_all("p"):
		if "推荐阅读" in p.get_text():
			p.decompose()
	return html

def getarturl(pageurl_list, proxy, driver):
	arturl_list = []
	for url in pageurl_list:
		try:
			driver.get(url)
			for i in range(2):
				try:
					element = driver.find_element_by_class_name(name="loadmore")
					element.click()
					time.sleep(3)
				except:
					print("加载完成")
					break
				content = BeautifulSoup(driver.page_source, "lxml")
				results = content.find_all(class_="left")[0].find_all("li")
				for result in results:
					art_time = "-".join(re.findall(r'(\d{4})-(\d{2})-(\d{2})', result.find(class_='info').get_text())[0])
					art_time = datetime.datetime.strptime(art_time, '%Y-%m-%d').date()
					aurl = result.h1.a["href"]
					if art_time >= (datetime.datetime.now() + datetime.timedelta(days=-1)).date():
						arturl_list.append(aurl)
		except:
			print("No page!")
	return arturl_list


def get_article(arturl_list, proxy, driver):
	for url in arturl_list:
		try:
			driver.get(url)
			content = BeautifulSoup(driver.page_source, "lxml").find_all(class_="left")[0]
			title = content.find_all(class_="title")[0].get_text()
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
				print("正在存储健康时报网“{0}”文章".format(title))
				pool.insert_one(
				"insert into article_classify.article_crawler(title,content,tags,channelId,categoryId,create_date) values (%s,%s,%s,%s,%s,%s)",
				(title, str(htmls), tags, channelId, categoryId, create_date))
		except:
			print("格式不一致")


def jksb_craw(proxy, driver):
	pageurl_list = getpageurl()
	arturl_list = getarturl(pageurl_list, proxy, driver)
	get_article(arturl_list, proxy, driver)


if __name__ == "__main__":
	get_proxy = GetProxy()
	option = webdriver.ChromeOptions()
	option.add_argument("headless")
	driver = webdriver.Chrome(chrome_options=option)
	proxy = get_proxy.get_proxy()
	jksb_craw(proxy, driver)

