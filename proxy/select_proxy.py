# coding: utf-8

import json
from configparser import ConfigParser

import requests

from mysql_pool import MySqlPool

cfg = ConfigParser()
cfg.read('../config.ini')
pool = MySqlPool(db='article_classify', host=cfg.get('mysql', 'host'), port=int(cfg.get('mysql', 'port')),
                 user=cfg.get('mysql', 'user'), passwd=cfg.get('mysql', 'password'))

class SelectProxy(object):

	def __init__(self, num):
		# 选择每次获取的proxy的数量
		self.MAX = num
		self.count = 0
		self.test_url = "http://ip.chinaz.com/getip.aspx"
		self.headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'}


	def test_proxy(self, testing_proxy):
		testing_proxy = {'http': 'http://' + testing_proxy }
		try:
			r = requests.get(url=self.test_url, proxies=testing_proxy, headers=self.headers, timeout=10)
			# print(r.content)
			return True
		except:
			return False

	def clear_proxy(self):
		pool.delete("delete from valid_proxy")

	def save_db(self, valid_proxy):
		"""
		存储有效代理
		:param valid_proxy:
		:return:
		"""
		pool.insert_one("insert into valid_proxy(proxy) VALUES(%s)",param=(valid_proxy))
		self.count += 1
		print('已存储%s条有效代理。' % self.count)

	def get_proxy_by_api(self):
		"""
		从代理api获取代理
		:return:
		"""
		# 订单号
		order_id = "557219260550567"
		# 提取数量
		num = self.MAX
		api = "http://tvp.daxiangdaili.com/ip/?tid=" + order_id + "&filter=on&num=" + str(num) + "&category=2&delay=1&foreign=none&format=json"
		r = requests.get(api)
		return r.content

	def engine(self):
		"""
		测试代理有效性并存入数据库
		:return:
		"""
		self.clear_proxy()
		proxy_content = self.get_proxy_by_api()
		proxy_json = json.loads(proxy_content)
		for record in proxy_json:
			proxy = str(record['host']) + ':' + str(record['port'])
			result = self.test_proxy(proxy)
			if result:
				self.save_db(proxy)
			else:
				# self.save_db(proxy + '   error')
				continue


if __name__ == "__main__":
	selectproxy = SelectProxy(100)
	selectproxy.engine()
