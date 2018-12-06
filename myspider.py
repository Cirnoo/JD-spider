import requests
import time
import csv
from bs4 import BeautifulSoup
from collections import OrderedDict
import re
class spider:
    def __init__(self):  
        name = '%E4%B8%89%E6%98%9F%E6%89%8B%E6%9C%BA'
        self.search_url='https://search.jd.com/Search?keyword='+name+'&enc=utf-8&page={0}'
        self.new_url='https://search.jd.com/s_new.php?keyword='+name+'&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq='+name+'&cid3=655&page={0}&s={1}&scrolling=y&log_id={2}'
        self.url=self.search_url
        self.head = {'authority': 'search.jd.com',
                'method': 'GET',
                'path': '/s_new.php?keyword='+name+'&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq='+name+'&cid2=653&cid3=655&page=4&s=84&scrolling=y&log_id=1529828108.22071&tpl=3_M&show_items=7651927,7367120,7056868,7419252,6001239,5934182,4554969,3893501,7421462,6577495,26480543553,7345757,4483120,6176077,6932795,7336429,5963066,5283387,25722468892,7425622,4768461',
                'scheme': 'https',
                'referer': 'https://search.jd.com/Search?keyword='+name+'&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&wq='+name+'&cid3=655&page=3&s=58&click=0',
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
                #'Cookie':'qrsc=3; pinId=RAGa4xMoVrs; xtest=1210.cf6b6759; ipLocation=%u5E7F%u4E1C; _jrda=5; TrackID=1aUdbc9HHS2MdEzabuYEyED1iDJaLWwBAfGBfyIHJZCLWKfWaB_KHKIMX9Vj9_2wUakxuSLAO9AFtB2U0SsAD-mXIh5rIfuDiSHSNhZcsJvg; shshshfpa=17943c91-d534-104f-a035-6e1719740bb6-1525571955; shshshfpb=2f200f7c5265e4af999b95b20d90e6618559f7251020a80ea1aee61500; cn=0; 3AB9D23F7A4B3C9B=QFOFIDQSIC7TZDQ7U4RPNYNFQN7S26SFCQQGTC3YU5UZQJZUBNPEXMX7O3R7SIRBTTJ72AXC4S3IJ46ESBLTNHD37U; ipLoc-djd=19-1607-3638-3638.608841570; __jdu=930036140; user-key=31a7628c-a9b2-44b0-8147-f10a9e597d6f; areaId=19; __jdv=122270672|direct|-|none|-|1529893590075; PCSYCityID=25; mt_xid=V2_52007VwsQU1xaVVoaSClUA2YLEAdbWk5YSk9MQAA0BBZOVQ0ADwNLGlUAZwQXVQpaAlkvShhcDHsCFU5eXENaGkIZWg5nAyJQbVhiWR9BGlUNZwoWYl1dVF0%3D; __jdc=122270672; shshshfp=72ec41b59960ea9a26956307465948f6; rkv=V0700; __jda=122270672.930036140.-.1529979524.1529984840.85; __jdb=122270672.1.930036140|85.1529984840; shshshsID=f797fbad20f4e576e9c30d1c381ecbb1_1_1529984840145'
            }
        self.goods_tab=OrderedDict()
        for i in range(1,5):
            print("page "+str(i)+'....')
            #self.get_first_page(i)
            self.get_second_page(i)
            print("***********")
        self.output()
    def output(self):
        with open('JD_Phone.csv','a',newline='',encoding='gbk')as f:
            write=csv.writer(f)
            for obj in self.goods_tab.values():
                obj.output(write)
    def get_goods_info(self,url):
        web = requests.get(url, headers=self.head)
        web.encoding='utf-8'
        html = web.text
        soup = BeautifulSoup(html,'lxml')
        lis = soup.find_all("li",class_="gl-item")
        for li in lis:
            id=int(li.get("data-pid"))
            if id not in self.goods_tab.keys():
                self.goods_tab[id]=goods_info(li)
            else:
                print("the same goods")
           
    def get_first_page(self,page):
        print("get the first 30...")
        url=self.search_url.format(page*2-1)
        self.get_goods_info(url)
    def get_second_page(self,page):
        print("get the later 30...")
        a=time.time()
        b='%.5f'%a
        n=page
        url=self.new_url.format(n,30*(n-1),b)
        self.get_goods_info(url)


class goods_info:
    def __init__(self,info):
        self.info=info
        self.name=self.get_name()
        self.url=self.get_url()
        self.price=self.get_price()
        self.ram=0
        self.battery=0
        self.color=self.get_color()
        #self.id=self.get_id()
    def get_name(self):
        return self.info.find("div",class_="p-name p-name-type-2").em.get_text()
    def get_url(self):
        return self.info.a.get("href")
    def get_id(self):
        return self.info.get("data-pid")
    def get_color(self):
        all_color=self.info.find_all("li",class_="ps-item")
        color=[]
        for c in all_color:
            color.append(c.a.get("title"))
        return color
    def get_price(self):
        return self.info.strong.get_text()
    def output(self,writer):
        writer.writerow([self.name,self.price,",".join(self.color),self.url])

if __name__=='__main__':
    with open('JD_Phone.csv','w+',newline='',encoding='gbk')as f:
        f.truncate()
    sp=spider()
