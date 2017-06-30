# -*- coding: utf-8 -*-
from __future__ import print_function
from sys import argv
import re
import urllib2

__author__ = 'frank'

# try:
url = argv['http://bbs.rednet.cn/thread-46157966-1-1.html']
# except Exception:
#     exit('url needed')

page = urllib2.urlopen(url).read() + '<link href=xxxx>'


def convert(_page):
    return _page


def get_page_charset(_page):
    return _page


def consistent_newline(_str):
    return _str.replace('\r\n', '\n').replace('\r', '\n')


def wipe_html_tags(_page_in_utf8):
    my_flag = re.IGNORECASE
    # doctype
    _content = re.sub(r'<!DOCTYPE.*?>', '', _page_in_utf8, flags=my_flag)
    # html tag
    _content = re.sub(r'<(\s|/)*?html.*?>', '', _content, flags=my_flag)
    # head tag
    _content = re.sub(r'<\s*?head.*?>(.*?\n)+.*?</+?head>', '', _content, flags=my_flag)
    # css links
    _content = re.sub(r'<.*?link[^\n]*', '', _content, flags=my_flag)
    # scripts
    _content = re.sub(r'<\s*?script.*?>(.|\n)*?</+?script.*?>', '', _content, flags=my_flag)
    # style tag
    _content = re.sub(r'<\s*?style.*?>(.|\n)*?</+?style.*?>', '', _content, flags=my_flag)
    # commnets
    _content = re.sub(r'<!--(.|\n)*?-->', '', _content, flags=my_flag)
    # entities
    _content = re.sub(r'&.{1,5};|&#.{1,5};', '', _content, flags=my_flag)
    # tags
    _content = re.sub(r'<([^>]|\n)+>', '', _content, flags=my_flag)
    # empty lines
    _content = re.sub(r'^\s*(?=\S)', '', _content, flags=my_flag)
    _content = re.sub(r'^\s*?\n', '', _content, flags=my_flag)
    return _content


def get_content(_lines, _block_length_array):
    content = ''
    for index, block_length in enumerate(_block_length_array):
        current_content = ''
        for index2, block_length2 in enumerate(_block_length_array[index:]):
            if block_length2 != 0:
                if _lines[index + index2].strip() != '':
                    current_content += _lines[index + index2] + '\n'
            else:
                break
        if len(current_content) > len(content):
            content = current_content
    return content


charset = get_page_charset(page)
page_in_utf8 = convert(page)

page_with_consistent_newline = consistent_newline(page_in_utf8)
page_without_html_tag = wipe_html_tags(page_with_consistent_newline)

lines = page_without_html_tag.split('\n')

block_length_array = [len(a) + len(b) + len(c) + len(d) + len(e) for a, b, c, d, e in
                      zip(lines, lines[1:], lines[2:], lines[3:], lines[4:])]

content = get_content(lines, block_length_array)

print(content)