# coding: utf-8
"""
Created on ****-**-**
@author: YangLei
@brief: 
@version: Anaconda Python 3.6
"""
import json
import urllib.parse
import urllib.request
from configparser import ConfigParser
from apscheduler.schedulers.blocking import BlockingScheduler
from mysql_pool import MySqlPool

schedudler = BlockingScheduler()
cfg = ConfigParser()
cfg.read('../config.ini')
pool = MySqlPool(db='yjk_data_etl',host=cfg.get('mysql','host'), port=int(cfg.get('mysql', 'port')),
                 user=cfg.get('mysql', 'user'), passwd=cfg.get('mysql', 'password'))

# def getArticle():
# 	values=pool.get_all("select id,title,content,tags,channelId,categoryId from article_classify.article_crawler where is_send is null ")
# 	return values

def getArticle():
	values=pool.get_all("select title,content,tags,image,createOperator from article_classify.article_crawler where is_send =99 ")
	return values

def sendArticle():
	#values = pool.get_all("select title,content,tags,image,createOperator from article_classify.article_crawler where is_send =99 limit 2")
	values=getArticle()
	i=0
	for value in values:
		# id=value['id']
		# if value['categoryId'] == None:
		# 	del value['categoryId']
		data = value
		print(data)
		# del data['id']
		headers = {'Content-Type': 'application/json'}
		results = json.dumps(data)
		try:
		#开发：http://192.168.1.168:8020/info/sync/bigData
		#hmp:http://hmpapi.ihaozhuo.com/info/sync/bigData
			request = urllib.request.Request(url='http://192.168.1.168:8020/info/sync/bigData', headers=headers,data=results.encode())
			response = urllib.request.urlopen(request)
			print(response.read().decode('utf-8'))
			i=i+1
			print("已发送{0}篇".format(i))
			# pool.update("update article_classify.article_crawler set is_send = %s where id = %s", param=(1, id))
		except:
			print("异常文章，过滤")


if __name__=="__main__":
	sendArticle()
	# schedudler.add_job(sendArticle, 'cron', day_of_week='0-6', hour=8, minute=30)
	# schedudler.start()
	