# coding: utf-8
"""
Created on ****-**-**
@author: YangLei
@brief: 老爸评测
@version: Anaconda Python 3.6
"""
import datetime
from configparser import ConfigParser

from bs4 import BeautifulSoup
from news_tags import get_channel, get_category, get_tags
from selenium import webdriver

from SaveToOss.DownloadSaveImage import DownloadSaveImage
from mysql_pool import MySqlPool
from proxy.get_proxy import GetProxy

cfg = ConfigParser()
cfg.read('config.ini')
pool = MySqlPool(db='yjk_data_etl', host=cfg.get('mysql', 'host'), port=int(cfg.get('mysql', 'port')),
                 user=cfg.get('mysql', 'user'), passwd=cfg.get('mysql', 'password'))

def getpageurl():
	url_list = ["https://daddylab.com/evaluation/p/"]
	pageurl_list = []
	for _ in url_list:
		for i in range(1,19):
			pageurl = _ +str(i)
			pageurl_list.append(pageurl)
	return pageurl_list

def get_time():
	now = datetime.datetime.now()
	create = now+datetime.timedelta(days=-1)
	return create.date()

def get_image_list(content):
	image_list=[]
	for _ in content.find_all("img"):
		image_list.append(_['src'])
	return image_list
	
def getarturl(pageurl_list, proxy, driver):
	arturl_list = []
	image_list=[]
	for url in pageurl_list:
		try:
			driver.get(url)
			content = BeautifulSoup(driver.page_source, "lxml")
			results = content.find_all(class_="content-blog")
			for result in results:
				arturl = "https://daddylab.com"+result.a["href"]
				image=result.img['src']
				arturl_list.append(arturl)
				image_list.append(image)
		except:
			print("No page!")
	return arturl_list,image_list


def get_article(arturl_list,image_list,proxy, driver):
	dsi = DownloadSaveImage()
	for i in range(len(arturl_list)):
		try:
			fir_image=image_list[i]
			fir_image_content=dsi.download(fir_image)
			fir_key,fir_url=dsi.get_file_path()
			dsi.oss_save(fir_key,fir_image_content)
			driver.get(arturl_list[i])
			content = BeautifulSoup(driver.page_source, "lxml").find_all(class_="row")[0]
			title = content.find_all(class_="title")[0].h3.get_text()
			create_date = datetime.datetime.now().date()
			html = content.find(class_='content')
			htmls=str(html)
			img_list=get_image_list(html)
			for _ in img_list:
				old=_
				img_content=dsi.download(_)
				save_key,save_url=dsi.get_file_path()
				#上传至oss
				dsi.oss_save(save_key,img_content)
				htmls=htmls.replace(old,save_url)
			context = html.get_text()
			tags = get_tags(title, context)
			channelId = get_channel(title, context)
			categoryId = get_category(channelId, tags)
			print("爬取文章处理中...")
			print("正在存储老爸评测“{0}”文章".format(title))
			pool.insert_one(
				"insert into article_classify.`article_crawler_2.0`(title,content,tags,channelId,categoryId,create_date,image) values (%s,%s,%s,%s,%s,%s,%s)",
				(title, htmls, tags, channelId, categoryId, create_date,fir_url))
		except:
			print("格式不一致")
		

def daddylab_craw(proxy, driver):
	pageurl_list = getpageurl()
	arturl_list,image_list = getarturl(pageurl_list,proxy, driver)
	get_article(arturl_list,image_list, proxy, driver)


if __name__ == "__main__":
	get_proxy = GetProxy()
	option = webdriver.ChromeOptions()
	option.add_argument("headless")
	driver = webdriver.Chrome(chrome_options=option)
	proxy = get_proxy.get_proxy()
	daddylab_craw(proxy, driver)
