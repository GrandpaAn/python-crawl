#-*- coding: utf-8 -*-
#encoding=utf-8
import urllib2
import urllib
import os
from BeautifulSoup import BeautifulSoup


def getAllUsername():
    html = urllib2.urlopen('http://8.7k7k.com/thread-141923-1-1.html').read()
    soup = BeautifulSoup(html)
    NameResult = soup.findAll('a',attrs={"class":"xw1"})
    Content = soup.findAll('td',attrs={"class":"t_f"})
    # print Content
    print NameResult


#     count = 0;
#     for image in liResult:
#         count += 1
#         link = image.get('src')
#         imageName = count
#         filesavepath = '/Desktop/testpython/%s.jpg' % imageName
#         urllib.urlretrieve(link,filesavepath)
#         print filesavepath 
if __name__ == '__main__':
    getAllUsername()

# from pyquery import PyQuery as pq
# doc = pq('http://bbs.duowan.com/thread-45199277-1-1.html')
# # print doc


# a = doc('a').filter(".xw1")

# a = a.decode("utf-8", 'ignore').encode('utf-8')
# print a.text().encode("utf-8")

# from pyquery import PyQuery as pq
# from lxml import etree

# doc = pq(filename='htmltest1.html')
# doc = pq(etree.fromstring("<html></html>"))
# # print doc
# # print doc.html()
# # print type(doc)
# li = doc('li')
# # print type(li)
# print li.text()

