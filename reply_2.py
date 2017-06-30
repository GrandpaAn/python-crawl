# -*- coding: utf-8 -*-
# __author__ = 'Bai Chenjia'
from selenium import webdriver
import re
import codecs

# 对爬虫爬取到的数据进行处理
def handel(content):
    raw_content = content.split('\n')
    raw_content = list(raw_content)
    #print "len", len(raw_content)
    if len(raw_content) < 3:
        #print "该数组为空"
        return "\n"
    else:
        for temp in raw_content:
            # 预处理只保留本层楼的评论，其他楼层的评论去除
            if temp == u"回复":
                index2 = raw_content.index(temp)
                raw_content.pop(index2)
                raw_content.pop(index2)
                raw_content.pop(index2)
                raw_content.pop(index2)
            #去除楼数
            if temp == "1" or temp == "2" or temp == "3" or temp == "4" or temp == "5" or temp == "6" or temp == "7" or temp == "8":
                index1 = raw_content.index(temp)
                raw_content.pop(index1-1)
                raw_content.pop(index1-1)
                raw_content.pop(index1-1)

        # 去除【此处隐藏..】这句话
        for temp in raw_content:
            #print "temp11", temp, type(temp)
            if re.match(ur"^[\u5df2\u7ecf\u9690\u85cf].*$", unicode(temp)):
                index3 = raw_content.index(temp)
                raw_content.pop(index3)

        # 从顶中提取数值
        for temp in raw_content:
            m = re.search(u"\u9876[^\d*?](\d*)\u005d", unicode(temp))
            if m:
                #print "temp11", temp
                index4 = raw_content.index(temp)
                raw_content[index4] = m.group(1)

        # 从踩中提取数值
        for temp in raw_content:
            m = re.search(u"\u8e29[^\d*?](\d*)\u005d", unicode(temp))
            if m:
                #print "temp11", temp
                index4 = raw_content.index(temp)
                raw_content[index4] = m.group(1)

    if len(raw_content) < 6:
        return raw_content   # 返回
    else:
        return "\n"


def Crawler(url):
    driver = webdriver.PhantomJS()
    driver.set_window_size(1120, 550)
    driver.get(url)
    fp = codecs.open("content.txt", 'wb', 'utf-8')

    #抓取第一页的数据
    contents = driver.find_elements_by_class_name("reply")  # 根据class抓取数据
    for content in contents:
        handel_data = handel(content.text)   # 调用处理函数返回一个list
        if handel_data == "\n":  # 如果为空
            continue
        else:
            fp.write("-----------------------------------------------------\n")
            for temp in handel_data:
                #print "temp22", temp, type(temp)
                fp.write(temp)
                fp.write('\n')
    print "进入第 1 页"
    page = 1
    #抓取第二页到尾页的数据
    flag = True
    while True:
        try:
            if flag:
                driver.find_element_by_link_text("下一页").click()   # 找到下一页的连接进入
            else:
                flag = True
        except:
            try:
                driver.find_element_by_link_text("下一页").click()   # 再尝试一次
            except:
                break
            else:
                flag = False
                continue
        else:
            page += 1
            print "进入第 " + str(page) + " 页"
            contents = driver.find_elements_by_class_name("reply")
            for content in contents:
                handel_data = handel(content.text)   # 调用处理函数
                if handel_data == "\n":  # 如果为空
                    continue
                else:
                    fp.write("-----------------------------------------------------\n")
                    for temp in handel_data:
                        #print "temp22", temp, type(temp)
                        fp.write(temp)
                        fp.write('\n')
    fp.close()
    driver.quit()

if __name__ == "__main__":
    url = "http://comment.news.163.com/news3_bbs/APLP5TVS00014JB6.html"  # 设定要抓取的网址
    Crawler(url)