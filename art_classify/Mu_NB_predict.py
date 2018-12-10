# coding: utf-8
"""
Created on ****-**-**
@author: YangLei
@brief:
@version: Anaconda Python 
"""
import jieba
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

def seg_corpus(title,content):
    con=title*200+content[0:200]
    content_seg = jieba.cut(con)
    corpus = " ".join(content_seg)
    return corpus

def vector_space(stop_word,corpus,train_idf=None):
	if train_idf is not None:
		trainbunch = train_idf
		vocabulary = trainbunch.vocabulary
		vectorizer = TfidfVectorizer(stop_words=stop_word, sublinear_tf=True, max_df=0.5,
		                             vocabulary=trainbunch.vocabulary)
		tdm = vectorizer.fit_transform([corpus])
	else:
		vectorizer = TfidfVectorizer(stop_words=stop_word, sublinear_tf=True, max_df=0.5)
		tdm = vectorizer.fit_transform([corpus])
		vocabulary = vectorizer.vocabulary_
	return tdm

def predict(title,content):
    sw_file = open("../dict/stopword.txt", encoding="utf-8")
    stop_word = sw_file.readlines()
    corpus = seg_corpus(title,content)
    train_set = joblib.load("../dict/train_set.dat")
    tdm = vector_space(stop_word,corpus,train_set)
    clf = joblib.load("../dict/model.m")
    channel = clf.predict(tdm)
    return channel


if __name__=="__main__":
    title="一头乌黑头发 离不开四款食疗方"
    content="很多人年纪轻轻就满头白发，想办法让自己的头发变的乌黑有亮泽，大家知道吃哪些食疗方是正解吗？这样的问题似乎困恼很多的朋友们，小编整理四款乌发食疗方，乌黑秀发有希望！乌发食疗方一，黑芝麻饮做法：50克的黑芝麻以及200克的黑豆，适量的枸杞和核桃，还有少许的米。将所以的食材一起煮制，这款食疗方除了乌发之外，还有补肾的功效呢？不过对于女性而言，想要乌发，还可以这样做：黑豆洗干净和米醋一起浸泡，待到10天之后来食用，非常适合女性乌发。二，首乌熬粥做法：制首乌少量，将其放在砂锅煮制然后取出汤汁，和粳米以及红枣熬粥，加入适量的糖即可享用。每天吃上两次，差不多一个月或者两个就会有效果的30天四个疗程）。相信大家对于首乌的功效是有一定认知的，和芝麻一样，它也是乌发比较有功效的食物，值得尝试！三，乌发茶饮做法：这是一款非常适合乌发的茶饮，这里面放入西红花、黑芝麻、桑葚以及绿茶、茯苓、枸杞等食物，一起磨碎制作出来的粉末，然后泡水来喝，非常适合大家进行乌发的。其实从材料可以看得出来，它确实有这样的作用。黑芝麻、西红花等。四，黑米粥做法：适量的黑米熬成粥，将适量的黑芝麻粉末加入其中，用余温来加热搅拌均匀，这样就可以食用了。而且这些食材都是比较简单就可以获得，平常觉得自己有白发的话，真的可以试试的！乌发的食物黑豆：黑豆这种食物从古时候就开始被作为乌发的一种食材，加之它在明目以及护肤上还有奇效，也是蛮受到欢迎的，如果搭配枸杞的话，乌发效果非常给力的！枸杞：白发的原因有很多种，其中就有肾虚的原因，而吃枸杞有很好的补肾作用，如果平常适量的吃些枸杞做出的食物，可以补肾的同时帮助头发黑回来呢？核桃：跟上面枸杞是同样的原理，也是在补肾的同时乌发。因为核桃有很好的固精强腰的作用，平常科学吃些核桃是可以帮助大家乌黑凉发。黑桑葚：桑葚确实也是很好的乌发的食物，除此之外，它在滋阴和生津方面的效果也是蛮强大的，而且这种食物并不难入口，大家可以当做零食食用。想要乌发吗？像通过饮食来进行食疗调理吗？那么就详细的看下本文，这些食疗以及食物是对大家乌发有帮助的。真心希望对于有白发问题的朋友，大家赶紧来看下本文吧，坚持的食用，您的黑发会重新出来的！其次，这些乌发的食物都是平常可以容易获得，也不是特别的贵或者难拿到，希望想要乌发的小伙伴赶紧来吧！"
    channel=predict(title,content)
    print(channel)
    # corpus=corpus(title,content)
    # train_set=joblib.load("train_set.dat")
    # tdm=vector_space(stop_word,corpus,train_set)
    # clf=joblib.load("model.m")
    # p=clf.predict(tdm)
    # print(p)


