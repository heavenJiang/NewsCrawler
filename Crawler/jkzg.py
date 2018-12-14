# coding: utf-8
"""
Created on ****-**-**
@author: YangLei
@brief: 健康中国APP健康科普栏抓取
@version: Anaconda Python 3.6
"""
import datetime
import json
import re
import time
from configparser import ConfigParser
from DelRepetition.isSame import isSame
from bs4 import BeautifulSoup
from selenium import webdriver
from SaveToOss.DownloadSaveImage import DownloadSaveImage
from art_classify.news_tags import get_channel, get_category, get_tags
from mysql_pool import MySqlPool
from proxy.get_proxy import GetProxy

cfg = ConfigParser()
cfg.read('../config.ini')
pool = MySqlPool(db='article_classify', host=cfg.get('mysql', 'host'), port=int(cfg.get('mysql', 'port')),
                 user=cfg.get('mysql', 'user'), passwd=cfg.get('mysql', 'password'))


def getpageurl():
	pageurl_list=[]
	for i in range(1,10):
		url="https://www.jkzg2030.com/ws-gj-jkzg/mobile/information/informationListNew/"+str(i)+"/4505"
		pageurl_list.append(url)
	return pageurl_list

def get_image_list(content):
	image_list = []
	for _ in content.find_all("img"):
		image_list.append(_['src'])
	return image_list

def chkChineseNum(title):
	num=0
	for word in title:
		if '\u4e00' <= word <= '\u9fff':
			num+=1
	return num

def getarturl(pageurl_list, proxy, driver):
	arturl_list = []
	topiclist=['皮肤科','减肥健身','亲子母婴','养生','饮食营养','口腔科','美容养颜','药膳食疗','两性','高血压']
	for url in pageurl_list:
		driver.get(url)
		content = json.loads(BeautifulSoup(driver.page_source, "lxml").get_text())
		for _ in content['data']['list']['data']:
			title=re.split(r'】|｜|\||丨',str(_['title']).strip())[-1].strip()
			url=_['shareUrl']
			topic=_['topicsName']
			if topic in topiclist and filtrate(title)==None:
				res=[title,url]
				arturl_list.append(res)
	return arturl_list

def filtrate(title):
	no_dict=['免费','直播','视频','医院','法','政策','国','省','市','党','政','名额','诊','参观','宣','专家','委','局','院','科','投票','手术','通知','节目','回顾']
	for word in no_dict:
		#过滤关键词
		if word in title:
			return False
		#过滤标题少于5个中文汉字的
		if chkChineseNum(title)<=5:
			return False
	
def get_article(arturl_list,proxy, driver):
	dsi = DownloadSaveImage()
	for i in range(len(arturl_list)):
		try:
			driver.get(arturl_list[i][1])
			driver.maximize_window()
			time.sleep(2)
			content = BeautifulSoup(driver.page_source, "lxml")
			title = arturl_list[i][0]
			create_date = "-".join(re.findall(r'(\d{4})-(\d{2})-(\d{2})',content.find_all(class_='subTitle')[0].get_text())[0])
			art_time = datetime.datetime.strptime(create_date, '%Y-%m-%d').date()
			if art_time >= (datetime.datetime.now() + datetime.timedelta(days=-1)).date():
				html = content.find(class_=re.compile('rich_media.*ng-scope'))
				htmls = str(html)
				img_list = get_image_list(html)
				for _ in img_list:
					old = _
					img_content = dsi.download(_)
					save_key, save_url = dsi.get_file_path()
					# 上传至oss
					dsi.oss_save(save_key, img_content)
					htmls = htmls.replace(old, save_url)
				context = html.get_text()
				tags = get_tags(title, context)
				channelId = get_channel(title, context)
				categoryId = get_category(channelId, tags)
				print("爬取文章{}".format(title))
				if isSame(title + context) is not False:
					print("正在存储健康中国“{0}”文章{1}".format(title,create_date))
					pool.insert_one(
						"insert into article_classify.article_crawler(title,content,tags,channelId,categoryId,create_date) values (%s,%s,%s,%s,%s,%s)",
						(title, str(htmls), tags, channelId, categoryId, create_date))
		except:
			print("格式不一致")

def jkzg_craw(proxy, driver):
	pageurl_list = getpageurl()
	arturl_list = getarturl(pageurl_list, proxy, driver)
	get_article(arturl_list,proxy,driver)


if __name__ == "__main__":
	get_proxy = GetProxy()
	option = webdriver.ChromeOptions()
	option.add_argument("headless")
	driver = webdriver.Chrome(chrome_options=option)
	proxy = get_proxy.get_proxy()
	jkzg_craw(proxy, driver)
