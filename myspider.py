#coding=utf-8
import requests
import time
import csv
from bs4 import BeautifulSoup
from collections import OrderedDict
import re
import json
class spider:
    def __init__(self):  
        name = '%E4%B8%89%E6%98%9F%E6%89%8B%E6%9C%BA'
        self.search_url='https://list.jd.com/list.html?cat=9987,653,655&ev=exbrand_15127&page={0}&sort=sort_rank_asc&trans=1&JL=6_0_0#J_main'
        self.url=self.search_url
        self.head = {'authority': 'search.jd.com',
                'method': 'GET',
                'path': '/s_new.php?keyword=%E4%B8%89%E6%98%9F%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&bs=1&ev=exbrand_%E4%B8%89%E6%98%9F%EF%BC%88SAMSUNG%EF%BC%89%5E&page=8&s=172&scrolling=y',
                'scheme': 'https',
                'referer': 'https://search.jd.com/Search?keyword=%E4%B8%89%E6%98%9F%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&bs=1&ev=exbrand_%E4%B8%89%E6%98%9F%EF%BC%88SAMSUNG%EF%BC%89%5E&page=7&s=133&click=0',
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
            }
        self.goods_url='https://item.jd.com/{0}.html'
        self.goods_tab=OrderedDict()
        for i in range(1,2):
            print("page "+str(i)+'....')
            self.get_per_page(i)
            print("***********")
        self.output()
    def output(self):
        with open('JD_Phone.csv','a',newline='',encoding='gb18030')as f:
            write=csv.writer(f)
            for obj in self.goods_tab.values():
                obj.output(write)
    def get_goods_info(self,url):
        web = requests.get(url, headers=self.head)
        web.encoding='utf-8'
        html = web.text
        soup = BeautifulSoup(html,'lxml')
        lis = soup.find_all("li",class_="gl-item")
        id_str=""
        id_list=[]
        for li in lis:
            str_t=li.div.get("data-sku")
            id=int(str_t)
            if id not in self.goods_tab.keys():
                self.goods_tab[id]=goods_info(li)
                id_str=id_str+str_t+','
                id_list.append(id)
            else:
                print("the same goods")
        self.set_price(id_str)
        self.set_goods_param(id_list)
    def set_goods_param(self,id_arr):
        for id in id_arr:
            url=self.goods_url.format(id)
            html=requests.get(url).text
            soup=BeautifulSoup(html,'lxml')
            self.goods_tab[id].set_param(soup)
    def set_price(self,id_str):
        json_url='https://p.3.cn/prices/mgets?skuIds='+id_str
        r = requests.get(json_url).text
        data = json.loads(r)
        for p in data:
            id=int(p['id'][2:])
            price=float(p['p'])
            self.goods_tab[id].price=price
    def get_per_page(self,page):
        print("get the first 30...")
        url=self.search_url.format(page)
        self.get_goods_info(url)
    def get_second_page(self,page):
        print("get the later 30...")
        a=time.time()
        b='%.5f'%a
        n=page
        url=self.new_url.format(n,31*int(n/2),b)
        self.get_goods_info(url)
class goods_info:
    def __init__(self,info):
        self.info=info
        self.id=self.get_id()
        self.name=None
        self.price=None
        self.ram=0
        self.battery=0
        self.color=[]
        self.battery=None
        self.camera_front=None
        self.camera_back=None
    def get_name(self):
        name=self.info.find("div",class_="p-name").em
        [s.extract() for s in name('span')]
        return ''.join(name.get_text().strip())
    def get_id(self):
        return int(self.info.div.get("data-sku"))
    def set_color(self,soup):
        t=soup.find('script').get_text()
        pos1=t.find('colorSize: [')
        if pos1==-1:
            return
        pos2=t[pos1:].find(']')
        begin=pos1+len('colorSize: [')
        end=pos1+pos2
        temp=t[begin:end]
        js=eval(temp)
        for c in js:
            self.color.append(c['颜色'])
    def set_name(self,soup):
        self.name=soup.find('div',class_="item ellipsis").get('title')
    def set_battery(self,soup):
        text=soup.find(text='电池容量（mAh）').next.get_text()
        self.battery=text+'mah'
    def set_param(self,soup):
        
        self.set_color(soup)
        self.set_name
        soup=soup.find('div',class_="detail")
        self.set_battery(soup)
        self.set_camera_frot(soup)
        self.set_camera_back(soup)
        self.set_ram(soup)
    def set_camera_frot(self,soup):
        label=None
        try:
            label=soup.find('dt',text='前置摄像头').next.next
        except:
            label=soup.find('td',text='前置摄像头').next.next
        self.camera_front=label.get_text
    def set_camera_back(self,soup):
        label=None
        try:
            label=soup.find('dt',text='后置摄像头').next.next
        except:
            label=soup.find('td',text='后置摄像头').next.next
        self.camera_front=label.get_text
    def set_ram(self,soup):
        label=soup.find(text='机型的运行内存，决定机身的运行速度。').parent.find_next()
        self.ram=label.get_text
    def output(self,writer):
        writer.writerow([self.name,self.price,",".join(self.color)])

if __name__=='__main__':
    with open('JD_Phone.csv','w+',newline='',encoding='gbk')as f:
        f.truncate()
    sp=spider()
