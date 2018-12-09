## Python 多线程京东爬虫

> 要求:抓取京东在售的三星手机的信息，信息包括：手机名称，价格，运行内存，电池容量，机身颜色，摄像头像素

* 本程序使用Python3.5，需要库
* 输出csv文件包含要求中的信息
* 不包含京东拍拍二手的商品

#### 需要的模块
* requests （获取网页源码）
* time	（sleep）
* csv	(输出.csv文件)
* BeautifulSoup	（HTML解析器）
* OrderedDict	（有序的字典）
* re	（正则表达式）
* json	（json格式化）
* threadpool,threading	（多线程）