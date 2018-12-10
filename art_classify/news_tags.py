# coding: utf-8
"""
Created on ****-**-**
@author: YangLei
@brief: 文章tags
@version: Anaconda Python 
"""
import multiprocessing
from configparser import ConfigParser
from multiprocessing import Pool

import jieba
import jieba.analyse as ana

from art_classify.Mu_NB_predict import predict
from mysql_pool import MySqlPool

cfg = ConfigParser()
cfg.read('../config.ini')
pool = MySqlPool(db='yjk_data_etl',host=cfg.get('mysql','host'), port=int(cfg.get('mysql', 'port')),
                 user=cfg.get('mysql', 'user'), passwd=cfg.get('mysql', 'password'))

def load_keywords():
	file = '../dict/keywords.txt'
	lines=open(file,encoding='utf-8').readlines()
	keywords=[]
	for line in lines:
		word=line.strip('\n')
		keywords.append(word)
	keywords=keywords[1::]
	return keywords

def get_tags(title,content):
    """
		自定义title中出现关键词权重较高
		:param corpus:
		:return:
		"""
    jieba.load_userdict('../dict/key_dict.txt')
    keywords = load_keywords()
    keyword_list = []
    titlelist = ana.extract_tags(title)
    for word in titlelist:
        if word in keywords:
            keyword_list.append(word)
        else:
            continue
    conlist = ana.extract_tags(content, topK=100)  # 取权重排序前100的关键词
    for word in conlist:
        if word in keywords and word not in keyword_list and len(keyword_list) <= 9:
            keyword_list.append(word)
        else:
            continue
    if keyword_list != []:
        tags = (',').join(keyword_list)
    else:
        keyword_list = ana.extract_tags(title+content, topK=5, allowPOS=('n'))
        tags = (',').join(keyword_list)
    return tags

def get_channelId(channel):
    id=pool.get_one("select channel_id from channel where name=%s",param=channel)
    return id['channel_id']

def get_channel(title,content):
    channel=predict(title,content)[0]
    channelId=get_channelId(channel)
    return channelId

def get_ccategorys(channelId):
    values=pool.get_all("select channel_id,name from channel where parent_id=%s",param=channelId)
    return values

def get_category(channelId,tags):
    values=get_ccategorys(channelId)
    if values is not False:
       categorys=list(i['name'] for i in values)
       for tag in tags.split(','):
           if tag in categorys:
               categoryId=get_channelId(tag)
               return categoryId

def GetNews(id):
	values=pool.get_all("select information_id,title,content from article where information_id=%s",param=id)
	for _ in values:
		id=_['information_id']
		title=_['title']
		content=_['content']
		tags=get_tags(title,content)
		channelId=get_channel(title,content)
		categoryId=get_category(channelId,tags)
		print("正在存储{0}的标签".format(id))
		update_keywords(id,tags,channelId,categoryId)

def update_keywords(id,tags,channelId,categoryId):
	pool.insert_one("insert into article_test(id,tags,channelId,categoryId) values (%s,%s,%s,%s)",(id,tags,channelId,categoryId))

if __name__=='__main__':
	lines=open("../dict/id.txt").readlines()
	p = multiprocessing.Pool(multiprocessing.cpu_count())
	for line in lines:
		id=line.strip('\n').strip('"')
		p.apply_async(GetNews, args=(id,))
	p.close()
	p.join()



