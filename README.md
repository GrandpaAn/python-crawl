# python-crawl

#### This code mianly about BBS website crawl.
#### 主要用到的方法：
####      1.将取到的文本进行预处理
####      2.获取标签，并用换行符代替
####      3.获取块
####      4.对每个块/停止词/链接/标点符号进行统计
####      5.通过和最小阈值进行对比获取最好的块，并获取其邻近的块
####      6.将最好的块和其邻近的块合并到一起
