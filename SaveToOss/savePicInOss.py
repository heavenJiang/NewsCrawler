# coding: utf-8
"""
Created on ****-**-**
@author: YangLei
@brief: 图片下载存储oss2接口
@version: Anaconda Python 2.7
"""
import requests
import time
import random
import oss2
from flask import Flask,request,jsonify,make_response
app=Flask(__name__)

def download(url):
	"""
	下载图片，返回一个二进制序列
	"""
	pic = requests.get(url)
	return pic.content


def get_file_path():
	"""
	生成图片存储key及访问url
	"""
	host = "http://yjk-article-image.img.aliyuncs.com/"
	date = time.strftime("%Y/%m/%d/", time.localtime())
	milli_time = str(int(round(time.time() * 1000)))
	end = str(random.randint(1000, 9999))
	key = "datag/" + date + milli_time + end + ".png"
	url = host + key
	return key, url

def oss_save(key, content):
	endpoint = 'http://oss-cn-hangzhou.aliyuncs.com'  # Suppose that your bucket is in the Hangzhou region.
	auth = oss2.Auth('LTAILE0ZHOIInqyY', 'tMmNtmzlzevZoIlH8ncQvdk2iRA7ST')
	bucket = oss2.Bucket(auth,endpoint, 'yjk-article-image')
	bucket.put_object(key, content)

@app.route('/savePicInOss',methods=['post'])
def savePicInOss():
	picurl=request.json.get('picurl')
	picContent=download(picurl)
	key, url=get_file_path()
	oss_save(key,picContent)
	return url


if __name__=="__main__":
	app.run()
	# print(savePicInOss("https://cdn.daddylab.com/Upload/image/20161123/20161123145310954.jpg"))