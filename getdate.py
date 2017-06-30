# -*- coding: utf-8 -*-
from BeautifulSoup import BeautifulSoup 
import urllib2
import re


date = re.compile(r'20\d{2}-\d+-\d+\s\d{2}:\d{2}')

url = 'http://bbs.9game.cn/thread-20674778-1-1.html'
req = urllib2.Request(url)
web = urllib2.urlopen(url).read()

result = re.search(date,web)

if result:
    print "publish_date:"+result.group(0)
else:
    print 'not match'

