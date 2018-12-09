#coding=utf-8
import requests
import time
import csv
from bs4 import BeautifulSoup
from collections import OrderedDict
import re
import json
import threadpool,threading

class spider:
    def __init__(self):  
        name = '%E4%B8%89%E6%98%9F%E6%89%8B%E6%9C%BA'
        self.search_url='https://list.jd.com/list.html?cat=9987,653,655&ev=exbrand_15127&page={0}&sort=sort_rank_asc&trans=1&JL=6_0_0#J_main'
        self.url=self.search_url
        self.head = {'authority': 'search.jd.com',
                'method': 'GET',
                'path': '/list.html?cat=9987,653,655&ev=exbrand_15127&page=1&sort=sort_rank_asc&trans=1&JL=6_0_0&callback=jQuery6136866&md=9&l=jdlist&go=0',
                'scheme': 'https',
                'referer': 'https://list.jd.com/list.html?cat=9987,653,655&ev=exbrand_15127&page=1&sort=sort_rank_asc&trans=1&JL=6_0_0',
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36',
                'x-requested-with': 'XMLHttpRequest',
            }
        self.pool=threadpool.ThreadPool(20) 
        self.goods_url='https://item.jd.com/{0}.html'
        self.goods_tab=OrderedDict()
        for i in range(1,7):    #一共6页
            print("page "+str(i)+'....')
            self.get_per_page(i)
            print("******page {0} ok*****".format(i))
        self.wait_thread_end()
        self.output()
    
    def output(self):
        with open('Samsung _Phone.csv','a',newline='',encoding='gb18030')as f:
            write=csv.writer(f)
            for obj in self.goods_tab.values():
                obj.output(write)

    def wait_thread_end(self):
        i=len(self.pool._requests_queue.queue)
        while (i>0):
            i=len(self.pool._requests_queue.queue)
            print('Waiting for worker threads...curent tasks {0}/20 '.format(i)) 
            time.sleep(0.8)
        self.pool.wait()

    """ def set_goods_param(self,id_arr):
        #单线程函数   
        for id in id_arr:
            url=self.goods_url.format(id)
            html=requests.get(url).text
            soup=BeautifulSoup(html,'lxml')
            self.goods_tab[id].set_param(soup) """
    
    def set_plus_param(self,id):
        #多线程函数
        try:
            url=self.goods_url.format(id)
            html=requests.get(url).text
            soup=BeautifulSoup(html,'lxml')
            cur_goods=self.goods_tab[id]
            cur_goods.set_param(soup)
        except NameError as e:
            print('Failure to Acquire goods Information id={0}'.format(id))
            print('行号：', e.__traceback__.tb_lineno)
            print('错误信息', e)   
    def set_price(self,id_str):
        json_url='https://p.3.cn/prices/mgets?skuIds='+id_str
        r = requests.get(json_url).text
        data = json.loads(r)
        for p in data:
            id=int(p['id'][2:])
            price=float(p['p'])
            if price<0:
                price='停售'
            self.goods_tab[id].price=price

    def get_per_page(self,page):
        print("get_goods_info.....")
        url=self.search_url.format(page)
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
        workers = threadpool.makeRequests(self.set_plus_param,id_list) 
        [self.pool.putRequest(req) for req in workers]

class goods_info:
    def __init__(self,info):
        self.id=self.get_id(info)
        self.name=None
        self.price=None
        self.ram=0
        self.battery=0
        self.color=[]
        self.battery=None
        self.camera_front=None
        self.camera_back=None
    def get_name(self,info):
        name=info.find("div",class_="p-name").em
        [s.extract() for s in name('span')]
        return ''.join(name.get_text().strip())
    def get_id(self,info):
        return int(info.div.get("data-sku"))
    def set_color(self,soup):
        # 如果有颜色选择列表，提取多个颜色
        try:
            try:
                t=soup.find('script').get_text()
                pos1=t.find('colorSize: [')
                assert(pos1>=0)
                pos2=t[pos1:].find(']')
                begin=pos1+len('colorSize: [')
                end=pos1+pos2
                temp=t[begin:end]
                json_ls=eval(temp)
                for c in json_ls:
                    self.color.append(c['颜色'])
                assert(len(self.color)>0)
            except AssertionError:  #提取一个颜色
                t=soup.find('dt',text='机身颜色').find_next()
                self.color.append(t.get_text())
        except : #无法获取颜色
            print('get color failure id={0}'.format(self.id))
            self.color.append('其他')
    def set_name(self,soup):
        try:
            # 提取名字方案一
            label=soup.find('div',class_="item ellipsis")
            if label!=None:
                self.name=label.get('title')
            else: # 方案二
                t=soup.find('div',class_='detail')
                self.name=t.find('div',class_="p-name").get_text()
            self.name=self.name.replace('三星（SAMSUNG） ','')
        except:
            print('set name error id={0}'.format(self.id))
    def set_battery(self,soup):
        try:
            text=soup.find(text='电池容量（mAh）')
            if text!=None:
                self.battery=text.next.get_text()
            else:
                self.battery=re.search('\d+mAh',soup.get_text(),re.IGNORECASE).group(0)
        except :
            print('get bettery failure id={0}'.format(self.id))
    def set_param(self,soup):
        self.set_color(soup)
        self.set_name(soup)
        soup=soup.find('div',class_="detail")
        self.set_battery(soup) 
        self.set_camera_frot(soup)
        self.set_camera_back(soup)
        self.set_ram(soup)
    
    def set_camera_frot(self,soup):
        try:
            label=soup.find('dt',text='前置摄像头')
            if label==None:
                label=soup.find('td',text='前置摄像头')
            if label==None: #奇葩商品页适用
                self.camera_front=re.search('前置摄像头\D*：(\d+.{0,10})\\n',soup.get_text()).group(1)
            else:
                self.camera_front=label.find_next().get_text()  
        except:
            print('set_camera_frot error id={0}'.format(self.id))
            self.camera_front='无'
    def set_camera_back(self,soup):
        try:
            label=soup.find('dt',text='后置摄像头')
            if label==None:
                label=soup.find('td',text='后置摄像头')
            if label==None: #奇葩商品页适用
                self.camera_back=re.search('后置摄像头\D*：(\D*\d+.{0,10})\\n',soup.get_text()).group(1)
            else:
                self.camera_back=label.find_next().get_text()  
        except:
            print('set_camera_back error id={0}'.format(self.id))
            self.camera_back='无'
    def set_ram(self,soup):
        try:
            label=soup.find(text='机型的运行内存，决定机身的运行速度。')    #方案一
            if label!=None:
                self.ram=label.parent.find_next().get_text()
            if self.ram=='其他' or label==None:   #方案一失败
                test=None
                test=re.search('\dG{0,1}B{0,1}(\+\d*GB{0,1})',soup.get_text(),re.IGNORECASE)
                if test==None:
                    test=re.search('(\d+G)RAM',soup.get_text(),re.IGNORECASE)
                if test!=None:
                    self.ram=test.group(1)
        except NameError as e:
            print("get ram failure id={0}".format(self.id))
            
    def output(self,writer):
        writer.writerow([self.name,self.price,str(",".join(self.color)),self.ram,self.battery,self.camera_front,self.camera_back])

if __name__=='__main__':
    with open('Samsung _Phone.csv','w+',newline='',encoding='gbk')as f:
        f.truncate()
        write=csv.writer(f)
        write.writerow(['型号','价格','颜色','RAM','电池容量','前置摄像头','后置摄像头'])
    sp=spider()
    