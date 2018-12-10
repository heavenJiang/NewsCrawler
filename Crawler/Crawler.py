# coding: utf-8
"""
Created on ****-**-**
@author: YangLei
@brief: 爬虫源调度
@version: Anaconda Python
"""
from gmw import gmw_craw
from hnwj import hnwj_craw
from jkb import jkb_craw
from jksb import jksb_craw
from kepuchina import kepuchina_craw
from selenium import webdriver
from wangyi import wangyi_craw
from cnr import cnr_craw
from health_huanqiu import health_huanqiu_craw
from health_people import health_people_craw
from proxy.get_proxy import GetProxy
from apscheduler.schedulers.blocking import BlockingScheduler
schedudler = BlockingScheduler()

def Crawler():
	get_proxy = GetProxy()
	driver = webdriver.PhantomJS()
	# 央广网
	proxy = get_proxy.get_proxy()
	cnr_craw(proxy, driver)
	#人民健康网
	proxy = get_proxy.get_proxy()
	health_people_craw(proxy, driver)
	#光明网
	proxy = get_proxy.get_proxy()
	gmw_craw(proxy, driver)
	#环球网
	proxy = get_proxy.get_proxy()
	health_huanqiu_craw(proxy, driver)
	#大河网
	proxy = get_proxy.get_proxy()
	hnwj_craw(proxy, driver)
	#健康报
	proxy = get_proxy.get_proxy()
	jkb_craw(proxy, driver)
	#健康时报
	proxy = get_proxy.get_proxy()
	jksb_craw(proxy, driver)
	#科普中国
	proxy = get_proxy.get_proxy()
	kepuchina_craw(proxy, driver)
	#网易健康
	proxy = get_proxy.get_proxy()
	wangyi_craw(proxy, driver)
	


if __name__ == "__main__":
	# schedudler.add_job(Crawler, 'interval', hours=8)
	# schedudler.start()
	Crawler()
	# schedudler.add_job(run, 'cron', day_of_week='0-6', hour=13, minute=23)
	# schedudler.start()
