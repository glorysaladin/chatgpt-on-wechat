# -*- coding: utf-8 -*-
import sys, re, os, time
import html5lib
import bs4
from bs4 import BeautifulSoup
import logging
import logging.handlers
import traceback
import urllib

import requests
import base64
import re
import random

#all_cookies=['_ga=GA1.1.617151142.1700845705; csrftoken=DjbuhsaiHvP003FQGYrJ8PpO7FOWx7tpDaScNNgSZPbFOtD0SqVffKD0Jf7TWevp; QianFanID=9xdisalghv3amslxrpfieag46qd7mp58; _ga_6Z94VT54DV=GS1.1.1700845704.1.1.1700845758.0.0.0', '_ga=GA1.1.1848973529.1699031414; csrftoken=0lHZKoZjyLt3oBkJGNiepOr2oRaFocOWTyEQbVzdnS3UxaqEVOgg38LKuPNqMS6p; QianFanID=xgd25v03suc75k86anq2g9lmvasa2me6; _ga_6Z94VT54DV=GS1.1.1700844413.9.1.1700844607.0.0.0', '_ga=GA1.1.2038213186.1700846044; csrftoken=OeHMiKKdetXqXyqOCCqxCug6Ylflwb6QeGQP7EqSVTffqUmXhM9QXNYGyED4LXD1; QianFanID=2utwyo6j62ii602k6hbpzwkykxaauvu7; _ga_6Z94VT54DV=GS1.1.1700927720.2.1.1700927933.0.0.0', '_ga=GA1.1.1037277109.1700928093; csrftoken=fSSuRuQyoJ6QZ4wTJQMpErgwjQ1GMu0PlcvlfFDgPXQpXZgJDFeDNLGVDPkactd7; QianFanID=012t6oh4o4cbrlk2oni9r137qyfnmq3u; _ga_6Z94VT54DV=GS1.1.1700928093.1.1.1700928354.0.0.0']
all_cookies=['_ga=GA1.1.682942178.1702266136; csrftoken=8FKGPdOK78XJt2E8QwHrvGx8PzyWknxPZr0ynKqURZ4fByhFAGMqm7v3RwXkLcHz; QianFanID=rh7x5ipgbi3ywczbioq15mug3jazfskz; _ga_6Z94VT54DV=GS1.1.1702266136.1.1.1702267904.0.0.0', '_ga=GA1.1.1251815640.1702268079; csrftoken=kSbheHZkYzzK81ZSdt880hmovssk50LakkQhEwvTKn5ynR3CJbZ3pSl4uDhYz53N; QianFanID=m5nrr678uf50akjt83cwd5wtydiw4ufa; _ga_6Z94VT54DV=GS1.1.1702268078.1.1.1702268120.0.0.0', '_ga=GA1.1.2017771551.1702268155; csrftoken=RNounHuuU0ZnvcyE0ymolee9MTrf1D39USf6QjNi0o7Ppe7XNfZJP29sKUKP8mce; QianFanID=f7p5ikljtcj76x3abyp2tnsts2ftpiyw; _ga_6Z94VT54DV=GS1.1.1702268154.1.1.1702268176.0.0.0', '_ga=GA1.1.1480452079.1702268204; csrftoken=GKy2nlfhdCID4tyqQcwXl1RYCwAAAo1S7ylw2UMWj7ZMpmygszbDcGwszfxtYAwa; QianFanID=f40a9xltk1gha1mpn2p21o5rlokm2jrz; _ga_6Z94VT54DV=GS1.1.1702268203.1.1.1702268226.0.0.0']
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
           'Cookie': '_ga=GA1.1.1920616457.1700845863; _ga_6Z94VT54DV=GS1.1.1700845863.1.0.1700845863.0.0.0; csrftoken=6Ldx0ATalNQ2mch3Pa3SelB2t8nRdRHs9Je5cZPoNWZN9u5JZe1qiE5tyWZIRxAv; QianFanID=jto7fmw7peb92sltfardk8ak3zjlwlfs'
}

session = requests.Session()
ROOT_URL="https://pan.qianfan.app"

def load_url(d, e):
    for b in e:
        if not str(b).isdigit():
            c = int(b, 16)
            d = d[:c] + d[c+1:c+10001]
    d = base64.b64decode(d)
    d = d.decode('utf-8', errors='ignore')
    return d

def good_match(s1, s2):
    set1 = set(s1)
    set2 = set(s2)
    common_chars = set1.intersection(set2)
    if len(common_chars)*1.0  / (len(set1) + 0.1) > 0.4:
       return True 
    return False

def _extract_movie_url(req_url, query, random_number):
    #print(req_url, query)
    try :
        headers['Cookie'] = all_cookies[random_number]
        resp = session.get(req_url, headers = headers)  ##  此处输入的url是登录后的豆瓣网页链接
        httpDoc = resp.text
        soup = None
        try:
            soup = BeautifulSoup(httpDoc, 'html5lib')
        except:
            soup = BeautifulSoup(httpDoc, 'html.parser')
        htmlNode = soup.html
        headNode = htmlNode.head
        bodyNode = htmlNode.body
        title_node = bodyNode.find("h1", attrs={"class":"item-detail-h1 search-title"})
        title=title_node.text
        info_node = bodyNode.find("div", attrs={"class":"item-detail-info"})
        url_node = info_node.find("div", attrs={"class":"copy-url pan-url btn-full btn"})
        pwd_node = info_node.find("div", attrs={"class":"copy-pwd btn-line btn"})
        url = ""
        # 解析url
        try:
            if url_node.has_key("data-url") and url_node.has_key("id"):
                data_url = url_node["data-url"]
                ids = url_node["id"]
                url = load_url(data_url, ids)
            if pwd_node is not None and pwd_node.has_key("data-pwd"):
                data_pwd=pwd_node["data-pwd"]
                url="{}?pwd={}".format(url, data_pwd)
        except:
            print(traceback.format_exc())
        # 解析网盘
        detail_node = info_node.find("div", attrs={"class":"item-detail-origin"})
        p_node = detail_node.find("p")
        file_count=""
        try:
            text=p_node.text.replace("\n","").replace(" ", "").replace("📁","")
            match = re.search(r'包含.*(\d+).*个文件', text)
            if match:
                file_count = match.group().replace("包含", "").replace('\xa0', '')
            else:
                print("没有找到匹配的文件个数")
        except:
            print(traceback.format_exc())
        if good_match(query, title):
            return "{} 【{}】\n{}".format(title, file_count, url)
        else:
            return None
    except:
        print(traceback.format_exc())
    return None

def _extract_page(req_url, random_number):
    urls = []
    try :
        headers['Cookie'] = all_cookies[random_number]
        resp = session.get(req_url, headers = headers)  ##  此处输入的url是登录后的豆瓣网页链接
        httpDoc = resp.text
        soup = None
        try:
            soup = BeautifulSoup(httpDoc, 'html5lib')
        except:
            soup = BeautifulSoup(httpDoc, 'html.parser')
        htmlNode = soup.html
        headNode = htmlNode.head
        bodyNode = htmlNode.body
        item_nodes = bodyNode.find_all("div", attrs={"class":"search-item"})
        for item_node in item_nodes:
            url_node = item_node.find("a")
            movie_page_url = "{}{}/".format(ROOT_URL, url_node["href"])
            urls.append(movie_page_url)
            img_node = item_node.find("img")
            title = img_node.text
            source = ""
            if img_node.has_key("alt"):
                source=img_node["alt"]
    except:
        pass
    return urls
def get_from_qianfan(query):
    random_number = random.randint(0, len(all_cookies) - 1)
    if "网盘" in query:
        query = query.replace("网盘", "")
    elif "云盘" in query:
        query = query.replace("云盘", "")
    if "夸克" in  query:
        query = query.replace("夸克", "") 
        feed_url="{}/search/?pan=quark&type=all&q={}".format(ROOT_URL, query)
    elif "百度" in query:
        query = query.replace("百度云", "") 
        query = query.replace("百度", "") 
        feed_url="{}/search/?pan=baidu&type=all&q={}".format(ROOT_URL, query)
    elif "阿里" in query:
        query = query.replace("阿里", "") 
        feed_url="{}/search/?pan=aliyundrive&type=all&q={}".format(ROOT_URL, query)
    elif "迅雷" in query:
        query = query.replace("迅雷", "") 
        feed_url="{}/search/?pan=xunlei&type=all&q={}".format(ROOT_URL, query)
    else:
        feed_url="{}/search/?pan=all&q={}".format(ROOT_URL, query)
    print(feed_url, query)
    urls=_extract_page(feed_url, random_number)
    final_rets = []
    for url in urls:
      ret= _extract_movie_url(url, query, random_number)
      if ret is not None:
          final_rets.append(ret)
    return final_rets
#print(get_from_qianfan("以爱为营"))
#movie_url='https://pan.qianfan.app/share/eyJtb2RlbCI6ImFsaXl1bmRyaXZlaW5mbyIsImlkIjoyNDUyODR9:omcB1Y52cd76ANQ3RGq8TkBXtKOlBKQQOyVWfWhNZT4'
#movie_url='https://pan.qianfan.app/share/eyJtb2RlbCI6ImFsaXl1bmRyaXZlaW5mbyIsImlkIjozMjA1NDh9:PZW0AMTvyH3Vv8BsAIr-1eQocRzrVipwNpZgHcp6xX4/'
#query="你好李焕英"
#print(_extract_movie_url(movie_url, query))
