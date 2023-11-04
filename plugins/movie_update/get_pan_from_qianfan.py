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

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36 OPR/66.0.3515.115'}
session = requests.Session()
ROOT_URL="https://pan.qianfan.app/"

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
    if len(common_chars)*1.0  / (len(set1) + 0.1) > 0.2:
       return True 
    return False

def _extract_movie_url(req_url, query):
    try :
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

def _extract_page(req_url):
    urls = []
    try :
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
            movie_page_url = "{}/{}".format(ROOT_URL, url_node["href"])
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
    urls=_extract_page(feed_url)
    final_rets = []
    for url in urls:
      ret= _extract_movie_url(url, query)
      if ret is not None:
          final_rets.append(ret)
    return final_rets
#print(get_from_qianfan("法医秦明夸克"))
