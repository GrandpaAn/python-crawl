#coding: utf-8
# creat by Grandpa An from 2017/5/1
# 
# 
# 
import re
import math
import urllib
import urllib2
from pyquery import PyQuery as pq
import sys

reload(sys)
sys.setdefaultencoding( "UTF-8" )
class UNiversalbbs(object):
	#设定一个最小长度的有效的块，根据经验将最小块的阈值设定为10
	min_block_len = 10
	## 论坛元数据所用的正则表达式
	_title = re.compile(r'<h1>(.*?)</h1>', re.I|re.S)
	_title2 = re.compile(r'<title>(.*?)</title>', re.I|re.S)
	_description = re.compile(r'<\s*meta\s*name=\"?Description\"?\s+content=\"?(.*?)\"?\s*>', re.I|re.S)
	_keywords = re.compile(r'<\s*meta\s*name=\"?Keywords\"?\s+content=\"?(.*?)\"?\s*>', re.I|re.S)
	# 特殊的情况
	_annotation_cases = [re.compile(r'<!-- 正文开头 -->(.*?)<!-- 正文结尾 -->'),]  #注释的正则表达式
	# 转义字符的正则表达式
	_special_list = [(re.compile(r'&quot;', re.I|re.S), '\"'),
			(re.compile(r'&amp;', re.I|re.S), '&'),
			(re.compile(r'&lt;', re.I|re.S), '<'),
			(re.compile(r'&gt;', re.I|re.S), '>'),
			(re.compile(r'&nbsp;', re.I|re.S), ' '),
			(re.compile(r'&#34;', re.I|re.S), '\"'),
			(re.compile(r'&#38;', re.I|re.S), '&'),
			(re.compile(r'&#60;', re.I|re.S), '<'),
			(re.compile(r'&#62;', re.I|re.S), '>'),
			(re.compile(r'&#160;', re.I|re.S), ' '),
			]
	_special_char = re.compile(r'&\w{2,6};|&#\w{2,5};', re.I|re.S)
	# html
	_html = re.compile(r'<\w*html', re.I|re.S)
	# DTD
	_doc_type = re.compile(r'<!DOCTYPE[^>]*?>', re.I|re.S)
	# html annotation
	_annotation = re.compile(r'<!--.*?-->', re.I|re.S)
	# js
	_javascript = re.compile(r'<script[^>]*?>.*?</script>', re.I|re.S)
	# css
	_css = re.compile(r'<style[^>]*?>.*?</style>', re.I|re.S)
	_ad_links = re.compile(r'(<a\s+[^>\"\']+href=[\"\']?[^>\"\']+[\"\']?\s+[^>]*>[^<>]{0,50}</a>\s*([^<>]{0,40}?)){2,100}', re.I|re.S) 
	_comment_links = re.compile(r'(<span[^>]*>[^<>]{0,50}</span>\s*([^<>]{0,40}?)){2,100}', re.I|re.S) 
	_link = re.compile(r'<a.*?>|</a>', re.I|re.S)
	_link_mark = '|linktag|'
	_paragraph = re.compile(r'<p(\s+[^>]+)??>|</p>|<br>', re.I|re.S)
	_special_tag = re.compile(r'<[^>\'\"]*[\'\"][^\'\"]{1,500}[\'\"][^>]*?>', re.I|re.S)
	#  匹配其余标签
	_other_tag = re.compile(r'<[^>]*?>', re.I|re.S)
	_new_line = re.compile(r'\r\n|\n\r|\r')
	_start_spaces = re.compile(r'^[ \t]+', re.M)
	_spaces = re.compile(r'[ \t]+')
	# _multi = re.compile(r'\n+')
	_multi = re.compile(r'\n|\r|\t')
	# punction
	_punc = re.compile(r',|\?|!|:|;|。|，|？|！|：|；|《|》|%|、|“|”', re.I|re.S)
	# stop words, specific for chinese pages
	_stopword = re.compile(r'备\d+号|Copyright\s*©|版权所有|all rights reserved|广告|推广|回复|评论|关于我们|链接|About|广告|下载|href=|本网|言论|内容合作|法律法规|原创|许可证|营业执照|合作伙伴|备案', re.I|re.S)
	def preprocess(self, text):         #将网页预处理
		text = self._new_line.sub(' ', text)
		for r , c in self._special_list:
			text = r.sub(c, text)
		text = self._special_char.sub(' ', text)
		text = self._doc_type.sub('', text)
		text = self._annotation.sub('', text)
		s = self._html.search(text)
		if not s: return ''
		if text.strip().startswith('document.write'): return ''
		return text

	def remove_tags(self, text):       #移除标签
		text = self._javascript.sub('\n', text)
		text = self._css.sub('\n', text)
		text = self._link.sub(self._link_mark, text)
		text = self._other_tag.sub('\n', text)
		text = self._start_spaces.sub('', text)
		text = self._spaces.sub(' ', text)
		return text

	def get_blocks(self, lines, thres): 
		 if not lines: return []
		 # for lin in lines:
		 #    print len(lin), lin
		 line_lens = [len(line) for line in lines]
		 tot_line = len(lines)

		 # get property block interval
		 empty_blocks = []
		 istart = 0
		 for iend in xrange(0, tot_line):
		 	if line_lens[iend] != 0 and iend > istart:
				empty_blocks.append( iend-istart-1 ) 
		 		start = iend
			if iend == tot_line - 1 and iend > istart:
		 		empty_blocks.append( iend-istart-1 ) 
		if not empty_blocks: return []
		sort_list = sorted(empty_blocks)
		sort_list2 = []
		for v in sort_list:
			if v > 1: sort_list2.extend([v] * v)
			else: sort_list2.append(v)
		prop_interval = max(3, sort_list2[len(sort_list2)/5]+1) 
		print 'interval:', prop_interval

		# get blocks 
		blocks = []
		istart = 0
		for iend in xrange(0, tot_line):
		 	if sum(line_lens[iend:iend+prop_interval]) <= 3 and iend > istart:
		 		if sum(line_lens[istart:iend]) >= thres: 
		 			blocks.append((istart, iend))
				istart = iend + prop_interval
		 		while istart < tot_line - 1 and line_lens[istart] <= 2:
		 			istart += 1
			if iend == tot_line - 1:
				if sum(line_lens[istart:iend]) >= thres: 
					blocks.append((istart, iend))
		return blocks

	def stat_blocks(self, lines, blocks):     ##得到文本块
		title_set = set(self.title.decode('utf-8', 'ignore'))
		title_len = len(title_set) + 1.0
		tot_line = len(lines)
		# 获得块的间隔
		block_scores = []
		for istart, iend in blocks:
			block = '\n'.join(lines[istart:iend]) 
			line_num = iend - istart + 1.0
			clean_block = block.replace(self._link_mark, '')

			position_rate = (tot_line - istart + 1.0) / (tot_line + 1.0)
		 	text_density = (len(clean_block) + 1.0) / line_num 
			punc_density = (len(self._punc.findall(clean_block)) + 1.0) / line_num 
			link_density = (block.count(self._link_mark) + 1.0) / line_num 
			stopword_density = (len(self._stopword.findall(clean_block)) + 1.0) / line_num 
			matched_set = set(clean_block.decode('utf-8', 'ignore')) & title_set
			title_match_rate = len(''.join(matched_set)) / title_len 
			# 获得块
			score = position_rate * text_density
			score *= math.pow(punc_density, 0.5)
			score *= 1.0 + title_match_rate
			score /= link_density
			score /= math.pow(stopword_density, 0.5)

			block_scores.append(score)
		return block_scores

	def extract_title(self, text):       #对网页标题进行解析，若_title提取不到h1，则用_title2来提取网页的title标签
		match = self._title.search(text)
		if not match:
		 	match = self._title2.search(text)
		if match:
			title = match.groups()[0]
			title = self._multi.sub(' ', title)
		else:
			return ''
		## 移除title中的噪声部分
		title_arr = re.split('\-|\||_', title) 
		title_scores = []
		for i, part in enumerate(title_arr):
			score = len(part.strip())
			score *= (len(title_arr) - i) / len(title_arr) 
			title_scores.append((i, score))
		sort_list = sorted(title_scores, key=lambda d:-d[1])
		new_title = ''
		for i in range((len(title_scores) + 1) / 2):
			new_title += ' ' + title_arr[sort_list[i][0]] 
		return new_title

	def extract_keywords(self, text):  #提取网站keywords
		match = self._keywords.search(text)
		if match:
			title = match.groups()[0]
			return self._multi.sub(' ', title)
		return ''

	def extract_description(self, text):    #解析网页的一些简短的描述，如注释
		match = self._description.search(text)
		if match:
			title = match.groups()[0]
			return self._multi.sub(' ', title)
		return ''

	def extract_content(self, text, thres):
		# 2. 获取标签，并用换行符代替
		text = self.remove_tags(text)

		# 3. 获取块
		lines = text.split('\n')
		# for line in lines: print line
		blocks = self.get_blocks(lines, thres)
		if not blocks: return ''

		# 4. 对每个块/停止词/链接/标点符号进行统计
		block_scores = self.stat_blocks(lines, blocks)

		# 5.  通过和最小阈值进行对比获取最好的块，并获取其邻近的块
		best_idx, best_block, best_score = -1, None, max(block_scores) - 1
		for i, score in enumerate(block_scores):
			if score > best_score:
				best_idx = i
				best_block = blocks[i]
				best_score = score

		# 6. 将最好的块和其邻近的块合并到一起
		i = best_idx - 1 
		while i >= 0:
			new_block = (blocks[i][0], best_block[1]) 
			new_score = self.stat_blocks(lines, [new_block])[0] 
			if new_score > best_score:
				best_score = new_score
				best_block = new_block
				i -= 1
			else:
				break
		i = best_idx + 1
		while i < len(blocks):
			new_block = (best_block[0], blocks[i][1]) 
			new_score = self.stat_blocks(lines, [new_block])[0] 
			if new_score > best_score:
				best_score = new_score
				best_block = new_block
				i += 1
			else:
				break

		content = '\n'.join(lines[best_block[0]:best_block[1]])
		content = self._multi.sub(' ', content) 
		content = content.replace(self._link_mark, '')
		return content

	def check_from_annotation(self, text):#对注释进行查找，并转为列表
		candi_list = []
		for r in self._annotation_cases: 
			s = r.search(text)
			if s:
				candi_list.extend(list(s.groups()))
		if not candi_list: return ''
		return '  '.join(candi_list)

	def extract(self, raw_text, _thres=0):
		if not raw_text: return '', '', '', ''

		# 1. remove newline characters
		text = self.preprocess(raw_text)

		self.title = self.extract_title(text)
		self.keywords = self.extract_keywords(text)
		self.desc = self.extract_description(text)

		# special process
		content = '' 
		if content:
			self.content = content
		else:
			self.content = self.extract_content(text, _thres or self.min_block_len)
		return [self.title, self.content, self.keywords, self.desc]

def download_and_normalize(url):   ##对网页进行下载，并对网页编码格式转为utf-8
	raw_html = urllib.urlopen(url).read()
	if not raw_html:
		return ''
	best_match = ('', 0)
	for charset in ['utf-8', 'gbk', 'big5', 'gb18030']:
		try:
			unicode_html = raw_html.decode(charset, 'ignore')
			guess_html = unicode_html.encode(charset)
			if len(guess_html) == len(raw_html):
				best_match = (charset, len(guess_html))
				break
			elif len(guess_html) > best_match[1]:
				best_match = (charset, len(guess_html))
		except: 
			pass
	raw_html = raw_html.decode(best_match[0], 'ignore').encode('utf-8')
	return raw_html

def get_reply():   ##获取评论，并写入文件
	urls = ['http://bbs.gfan.com/android-8397839-1-1.html']
	for url in urls:
		doc1 = pq(url)('div').filter(".pct")
		doc1
		# doc2 = 
		f = open('test.txt','a')
		for css in doc1:
			print >>f,'{reply:}{\n',pq(css)('td').text(),'}'
		f.close()

def get_date():  ##获取发表时间，并写入文件
	urls = ['http://bbs.gfan.com/android-8397839-1-1.html']
	for url in urls:
		_datetime = re.compile(r'20\d{2}-\d+-\d+\s\d{2}:\d{2}|20\d{2}-\d+-\d+\s\d{2}:\d{2}:\d{2}')
		req = urllib2.Request(url)
		web = urllib2.urlopen(url).read()
		f = open('test.txt','a')
		result = re.search(_datetime,web)
		if result:
			print >>f, "{post_date:}{",result.group(0),"}"
		else:
			print >>f, 'not match'
		f.close()

def get_author():  ##获得作者，并写入文件
	urls = ['http://bbs.gfan.com/android-8397839-1-1.html']
	for url in urls:    
		doc1 = pq(url)('td').filter(".pls")
		doc2 = pq(url)('td').filter(".post_author")
		doc3 = pq(url)('td').filter(".postauthor")
		doc4 = pq(url)('td').filter(".floot_left")
		f = open('test.txt','a')
		print >>f,'{author}:{\n',pq(doc1)('a').eq(0).text().encode("utf-8").replace("\n", ""),'}'
		print >>f,'{author}:{\n',pq(doc2)('a').eq(0).text().encode("utf-8").replace("\n", ""),'}'
		print >>f,'{author}:{\n',pq(doc3)('a').eq(0).text().encode("utf-8").replace("\n", ""),'}'
		print >>f,'{author}:{\n',pq(doc4)('a').eq(0).text().encode("utf-8").replace("\n", ""),'}'
		f.close()

def test():  ##把网页的url、title、内容写入文件
	ext = UNiversalbbs()
	urls = ['http://bbs.gfan.com/android-8397839-1-1.html']
	f = open('test.txt','a')
	for url in urls:
		raw_html = download_and_normalize(url)
		if raw_html:
			print >>f,'{url:}{',url,'}'
			for i in xrange(0, 10):
				title, content, keywords, desc= ext.extract(raw_html)
			print >>f,'{title:}{\n', title,'}'            
			print >>f,'{content:}{\n', content,'}'        
		else:
			print '\n{url:}{', url,'}'
			print 'error_msg:', err    
	f.close()

if __name__ == '__main__':
	impor sys
	if  len(sys.argv) == 2:
		test_file(sys.argv[1])
	else:
		test()
		get_date()
		get_author()
		get_reply()
