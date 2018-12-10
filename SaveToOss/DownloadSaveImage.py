# coding: utf-8
"""
Created on ****-**-**
@author: YangLei
@brief: 图片上传存储oss
@version: Anaconda Python 3.6
"""
import requests
import time
import random
import oss2

class DownloadSaveImage():
	def __init__(self):
		self.endpoint = 'http://oss-cn-hangzhou.aliyuncs.com'  # Suppose that your bucket is in the Hangzhou region.
		self.auth = oss2.Auth('LTAILE0ZHOIInqyY', 'tMmNtmzlzevZoIlH8ncQvdk2iRA7ST')
		self.bucket = oss2.Bucket(self.auth, self.endpoint, 'yjk-article-image')
	def download(self,url):
		"""
		下载图片，返回一个二进制序列
		:param url:
		:return:
		"""
		pic=requests.get(url)
		return pic.content
	
	def get_file_path(self):
		"""
		生成图片存储key及访问url
		:return:
		"""
		host="http://yjk-article-image.img.aliyuncs.com/"
		date = time.strftime("%Y/%m/%d/", time.localtime())
		milli_time = str(int(round(time.time() * 1000)))
		end = str(random.randint(1000, 9999))
		key = "datag/" + date + milli_time + end + ".png"
		url=host+key
		return key,url
	
	def oss_save(self,key,content):
		self.bucket.put_object(key,content)
	
	
if __name__=="__main__":
	dsi=DownloadSaveImage()
	pic=dsi.download("https://cdn.daddylab.com/Upload/image/20161123/20161123145310954.jpg")
	key,url=dsi.get_file_path()
	print(key,url)
	# dsi.oss_save(key,pic)
	# print(url)