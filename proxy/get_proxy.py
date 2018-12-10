# coding: utf-8
import random
from configparser import ConfigParser

from mysql_pool import MySqlPool
from proxy.select_proxy import SelectProxy

cfg = ConfigParser()
cfg.read('../config.ini')
pool = MySqlPool(db='article_classify', host=cfg.get('mysql', 'host'), port=int(cfg.get('mysql', 'port')),
                 user=cfg.get('mysql', 'user'), passwd=cfg.get('mysql', 'password'))

class GetProxy(object):

	def __init__(self):
		self.select_proxy = SelectProxy(1)

	def get_proxy(self):
		"""
		从数据库中批量抽取代理，选取任一代理，并再次验证，最终返回有效代理
		:return: 任一有效代理
		"""
		values=pool.get_all("SELECT proxy FROM valid_proxy")
		db_proxies = [p['proxy'] for p in values]
		random_proxy = random.sample(db_proxies, 1)[0]
		proxy = {"http": "http://" + random_proxy}
		return proxy

if __name__ == "__main__":
	proxy = GetProxy()
	result = proxy.get_proxy()
	print(result)

