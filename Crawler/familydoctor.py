# coding: utf-8
"""
Created on ****-**-**
@author: YangLei
@brief: 家庭医生在线
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
	pageurl_list = ['http://yinshi.familydoctor.com.cn/yyzd/scda/',
	                'http://zy.familydoctor.com.cn/zyts/zyys/',
	                'http://sex.familydoctor.com.cn/xsh/xxl/',
	                'http://yangsheng.familydoctor.com.cn/jksh/zs/',
	                'http://yangsheng.familydoctor.com.cn/zyys/',
	                'http://zy.familydoctor.com.cn/zyts/yssl/',
	                'http://lady.familydoctor.com.cn/nrbj/rcbj/',
	                'http://lady.familydoctor.com.cn/nrqg/xljq/',
	                'http://lady.familydoctor.com.cn/nrqg/xljq/',
	                'http://beauty.familydoctor.com.cn/hf/jq/',
	                'http://lady.familydoctor.com.cn/nrbj/bjwq/',
	                'http://lady.familydoctor.com.cn/nrbj/bwbj/',
	                'http://lady.familydoctor.com.cn/nrbj/yyys/',
	                'http://yangsheng.familydoctor.com.cn/yszd/sj/',
	                'http://yangsheng.familydoctor.com.cn/yszd/jb/',
	                'http://yangsheng.familydoctor.com.cn/ysmj/cs/',
	                'http://yangsheng.familydoctor.com.cn/ysmj/nr/',
	                'http://yangsheng.familydoctor.com.cn/ysmj/nanr/']
	return pageurl_list

def DescArt(html):
	for img in html.find_all("img"):
		img.decompose()
	for p in html.find_all("p"):
		if "推荐阅读" in p.get_text():
			p.decompose()
	return html

def getarturl(pageurl_list, proxy, driver):
	arturl_list = []
	for url in pageurl_list:
		driver.get(url)
		content = BeautifulSoup(driver.page_source, "lxml")
		if content.find_all(class_=re.compile("module\smainList"))!=[]:
			results = content.find_all(class_=re.compile("module\smainList"))[0].find_all("dl")
			for result in results:
				art_time = "-".join(re.findall(r'(\d{4})-(\d{2})-(\d{2})', result.find_all("span")[1].get_text())[0])
				art_time = datetime.datetime.strptime(art_time, '%Y-%m-%d').date()
				arturl =result.find_all("p")[1].a["href"]
				if art_time >= (datetime.datetime.now() + datetime.timedelta(days=-1)).date():
					arturl_list.append(arturl)
		else:
			results = content.find_all(class_=re.compile("module\smNyList"))[0].find_all(class_="text")
			for result in results:
				art_time = "-".join(re.findall(r'(\d{4})-(\d{2})-(\d{2})', result.find(class_="more").get_text())[0])
				art_time = datetime.datetime.strptime(art_time, '%Y-%m-%d').date()
				arturl = result.find(class_="textContent").p.a["href"]
				if art_time >= (datetime.datetime.now() + datetime.timedelta(days=-1)).date():
					arturl_list.append(arturl)
	return arturl_list

def get_article(arturl_list, proxy, driver):
	for url in arturl_list:
		try:
			driver.get(url)
			content = BeautifulSoup(driver.page_source, "lxml").find_all(class_="colL")[0]
			title = content.find_all(class_="article-titile")[0].h1.get_text()
			timesoup = str(content.find_all(class_="left")[0].get_text)
			create_date = "-".join(re.findall(r'(\d{4})年(\d{2})月(\d{2})日', timesoup)[0])
			create_date = datetime.datetime.strptime(create_date, '%Y-%m-%d').date()
			html = content.find(class_='viewContent')
			ad=content.find(class_="adLeftPip")
			ad.decompose()
			html=DescArt(html)
			htmls=str(html)
			a=html.find_all("a")
			for _ in a:
				htmls=htmls.replace(str(_),_.get_text())
			context = html.get_text()
			tags = get_tags(title, context)
			channelId = get_channel(title, context)
			categoryId = get_category(channelId, tags)
			print("爬取文章{}".format(title))
			if isSame(title + context) is not False:
				print("正在存储家庭医生“{0}”文章".format(title))
				pool.insert_one(
					"insert into article_classify.article_crawler(title,content,tags,channelId,categoryId,create_date) values (%s,%s,%s,%s,%s,%s)",
					(title, str(htmls), tags, channelId, categoryId, create_date))
		except:
			print("格式不一致")


def familydoctor_craw(proxy, driver):
	pageurl_list = getpageurl()
	arturl_list = getarturl(pageurl_list, proxy, driver)
	get_article(arturl_list, proxy, driver)


if __name__ == "__main__":
	get_proxy = GetProxy()
	option = webdriver.ChromeOptions()
	option.add_argument("headless")
	driver = webdriver.Chrome(chrome_options=option)
	proxy = get_proxy.get_proxy()
	familydoctor_craw(proxy, driver)

