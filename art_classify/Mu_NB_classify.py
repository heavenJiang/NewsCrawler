# coding: utf-8
"""
Created on 2018-06-14
@author: YangLei
@brief: 朴素贝叶斯多项式模型分类
@version: Anaconda Python 3.6
"""
from configparser import ConfigParser

import jieba
import numpy as np
from sklearn import metrics
from sklearn.datasets.base import Bunch
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.naive_bayes import MultinomialNB

from mysql_pool import MySqlPool

cfg=ConfigParser()
cfg.read('../config.ini')
pool=MySqlPool(db="article_classify",host=cfg.get("mysql","host"),
			   port=int(cfg.get("mysql","port")),
			   user=cfg.get("mysql","user"),
			   passwd=cfg.get("mysql","password"))

def load_data():
	"""
	加载数据集
	:return:
	"""
	values=pool.get_all("select * from trainset")
	corpus=[]
	for _ in values:
		content=str(_['title']*200+_['content'][0:200])
		label=_['label']
		res=[content,label]
		corpus.append(res)
	return np.array(corpus)

def split_data_2(corpus):
	"""
	均匀划分训练集与测试集
	:param corpus:
	:return:
	"""
	x=corpus[:,0]#训练数据集
	y=corpus[:,1]#类别数据集
	ss = StratifiedShuffleSplit(test_size=0.1, train_size=0.9, random_state=0)
	for train_index,test_index in ss.split(x,y):
		train=corpus[train_index]
		test=corpus[test_index]
		return train,test

def get_class_distribution(y):
	"""
	统计类别分布
	:param y: 类别标签
	:return: 返回一个字典，键是类别标签，值是这类记录数占总数的百分比分布
	"""
	d = {}
	set_y = set(y)
	for y_label in set_y:
		no_elements = len(np.where(y == y_label)[0])
		d[y_label] = no_elements
	dist_percentage = {class_label: count/(1.0*sum(d.values())) for class_label, count in d.items()}
	return dist_percentage

def print_class_label_split(train, test):
	#数据集描述
	print('Original Dataset size: {}'.format(corpus.shape))
	print('Train size: {}'.format(train.shape))
	print('Test size: {}'.format(test.shape))
	#训练集类别分布
	y_train=train[:,-1]
	train_distribution=get_class_distribution(y_train)
	print("\nDistribution of Train set:")
	for d in train_distribution:
		print("label=%s,percent=%.2f"%(d,train_distribution[d]))
	# 测试集类别分布
	y_test = test[:, -1]
	test_distribution = get_class_distribution(y_test)
	print("\nDistribution of Test set:")
	for d in test_distribution:
		print("label=%s,percent=%.2f" % (d, test_distribution[d]))

def corpus_segment2bunch(data):
	"""
	构建分词后的文本对象
	:param data:
	:return:
	"""
	catlist=set(data[:,1])
	bunch=Bunch(target_name=[],label=[],content=[])
	bunch.target_name.extend(catlist)
	for cat in catlist:
		for i in range(len(data)):
			if data[i][1]==cat:
				label=cat
				content_seg=jieba.cut(data[i][0])
				content=" ".join(content_seg)
				bunch.label.append(label)
				bunch.content.append(content)
	return bunch

def vector_space(stop_word,bunch,train_idf=None):
	"""
	构建词向量
	:param stop_word:
	:param bunch:
	:param train_idf:
	:return:
	"""
	tfidfspace = Bunch(target_name=bunch.target_name, label=bunch.label,tdm=[],vocabulary={})
	if train_idf is not None:
		trainbunch = train_idf
		tfidfspace.vocabulary = trainbunch.vocabulary
		vectorizer = TfidfVectorizer(stop_words=stop_word, sublinear_tf=True, max_df=0.5,
		                             vocabulary=trainbunch.vocabulary)
		tfidfspace.tdm = vectorizer.fit_transform(bunch.content)
	else:
		vectorizer = TfidfVectorizer(stop_words=stop_word, sublinear_tf=True, max_df=0.5)
		tfidfspace.tdm = vectorizer.fit_transform(bunch.content)
		tfidfspace.vocabulary = vectorizer.vocabulary_
	return tfidfspace

def metrics_result(actual, predict):
    print('精度:{0:.3f}'.format(metrics.precision_score(actual, predict,average='weighted')))
    print('召回:{0:0.3f}'.format(metrics.recall_score(actual, predict,average='weighted')))
    print('f1-score:{0:.3f}'.format(metrics.f1_score(actual, predict,average='weighted')))

if __name__=='__main__':
	corpus=load_data()
	train,test=split_data_2(corpus)
	#打印数据集划分情况
	# print_class_label_split(train, test)
	#训练集文本对象
	train_bunch=corpus_segment2bunch(train)
	sw_file=open("../dict/stopword.txt",encoding="utf-8")
	stop_word=sw_file.readlines()
	train_set=vector_space(stop_word,train_bunch)
	with open("train_set.dat","wb") as file_obj:
		joblib.dump(train_set,file_obj)
	# 测试集文本对象
	test_bunch=corpus_segment2bunch(test)
	test_set=vector_space(stop_word,test_bunch,train_set)
	# 训练分类器：输入词袋向量和分类标签
	clf = MultinomialNB(alpha=0.4).fit(train_set.tdm, train_set.label)
	# 预测分类结果
	predicted = clf.predict(test_set.tdm)
	for flabel,expct_cate in zip(test_set.label,predicted):
		if flabel != expct_cate:
			print(": 实际类别:", flabel, " -->预测类别:", expct_cate)
	metrics_result(test_set.label, predicted)
	joblib.dump(clf,"model.m")










