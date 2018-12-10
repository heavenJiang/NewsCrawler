# coding: utf-8
"""
Created on ****-**-**
@author: YangLei
@brief: 去重算法——simhash
@version: Anaconda Python 3.6
"""
# -*- coding: utf-8 -*-
import jieba
import jieba.analyse
import numpy as np
import json

class simhash:
	"""
	算法流程：
	·分词
		给定一段语句，进行分词，得到有效的特征向量，然后为每一个特征向量设置1-5等5个级别的权重（如果是给定一个文本，那么特征向量可以是文本中的词，
		其权重可以是这个词出现的次数）。
	·hash
		通过hash函数计算各个特征向量的hash值，hash值为二进制数01组成的n-bit签名。
	·加权
		在hash值的基础上，给所有特征向量进行加权，即W = Hash * weight，且遇到1则hash值和权值正相乘，遇到0则hash值和权值负相乘。
	·合并
		将上述各个特征向量的加权结果累加，变成只有一个序列串。拿前两个特征向量举例，
	·降维
		对于n-bit签名的累加结果，如果大于0则置1，否则置0，从而得到该语句的simhash值，最后我们便可以根据不同语句simhash的海明距离来判断它们的相似度。
	"""
	def __init__(self, content):
		self.simhash = self.simhash(content)
	
	def __str__(self):
		return str(self.simhash)
	
	def simhash(self, content):
		seg = jieba.cut(content)
		jieba.analyse.set_stop_words('../dict/stopword.txt')
		keyWord = jieba.analyse.extract_tags('|'.join(seg), topK=50, withWeight=True, allowPOS=())  # 在这里对jieba的tfidf.py进行了修改
		# 将tags = sorted(freq.items(), key=itemgetter(1), reverse=True)修改成tags = sorted(freq.items(), key=itemgetter(1,0), reverse=True)
		# 即先按照权重排序，再按照词排序
		keyList = []
		for feature, weight in keyWord:
			weight = int(weight * 20)
			feature = self.string_hash(feature)
			temp = []
			for i in feature:
				if (i == '1'):
					temp.append(weight)
				else:
					temp.append(-weight)
			keyList.append(temp)
		list1 = np.sum(np.array(keyList), axis=0)
		if (keyList == []):  # 编码读不出来
			return '00'
		simhash = ''
		for i in list1:
			if (i > 0):
				simhash = simhash + '1'
			else:
				simhash = simhash + '0'
		return simhash
	
	def string_hash(self, source):
		if source == "":
			return 0
		else:
			x = ord(source[0]) << 7
			m = 1000003
			mask = 2 ** 128 - 1
			for c in source:
				x = ((x * m) ^ ord(c)) & mask
			x ^= len(source)
			if x == -1:
				x = -2
			x = bin(x).replace('0b', '').zfill(64)[-64:]
			return str(x)

	def hammingDis(self, com):
		t1 = '0b' + self.simhash
		t2 = '0b' + com.simhash
		n = int(t1, 2) ^ int(t2, 2)
		i = 0
		while n:
			n &= (n - 1)
			i += 1
		return i

if __name__=="__main__":
	content="去黑头 维A酸最有效 "
	si=simhash(content)
	print(si.hammingDis(simhash("去黑头 维A酸最有效吧可以的")))
	
