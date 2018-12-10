# coding: utf-8
"""
Created on ****-**-**
@author: YangLei
@brief: 去掉已爬数据库的重复文章
@version: Anaconda Python 3.6
"""

import pickle as p
from configparser import ConfigParser
from bs4 import BeautifulSoup
from DelRepetition.SimiHash import simhash
from mysql_pool import MySqlPool

cfg = ConfigParser()
cfg.read('../config.ini')
pool = MySqlPool(db='article_classify', host=cfg.get('mysql', 'host'), port=int(cfg.get('mysql', 'port')),
                 user=cfg.get('mysql', 'user'), passwd=cfg.get('mysql', 'password'))


def hdist(simi, content):
	si=simhash(content)
	if simi==[]:
		return si
	else:
		for _ in simi:
			if si.hammingDis(_)<=5:
				return False
	return si

def Train():
	values = pool.get_all("select id,title,content from article_crawler")
	simi = []
	for _ in values:
		content = _['title']+BeautifulSoup(_['content'],"lxml").get_text().strip()
		si = hdist(simi, content)
		if si is False:
			print("删除重复文本{0}".format(_['id']))
			pool.delete("delete from article_crawler where id=%s",param=(_['id']))
		else:
			simi.append(si)
	print(len(simi))
	simListfile="../dict/simList.data"
	f = open(simListfile, 'wb')
	p.dump(simi, f)
	f.close
	
def isSame(content):
	f = open("../dict/simList.data",'rb')
	simList = p.load(f)
	if hdist(simList,content) is not False:
		simList.append(hdist(simList,content))
		p.dump(simList,open("../dict/simList.data",'wb'))
	else:
		print("文章重复，过滤！")
		return False
	
if __name__ == "__main__":
	# print(isSame("还在给宝宝傻傻补钙？这个东西才是宝妈们急需重视的!"))
	Train()
	# f = open("simList.data", 'rb')
	# simList = p.load(f)
	# print(len(simList))
