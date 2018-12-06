from bs4 import BeautifulSoup
import csv
import re
import string
from collections import OrderedDict
class goods_info:
    def __init__(self,soup):
        self.name=""
        self.url=""
        self.price=0
        self.ram=0
        self.battery=0
        self.color=""
    def get_name(self,soup):
        return soup.a.em.text
    def get_price(self,soup):
        return 0
te=OrderedDict()
te[100]="ss"
te[20]='sss'
for i in te.keys():
    print(te[i])
#print(soup.find(text=emailid_regexp))