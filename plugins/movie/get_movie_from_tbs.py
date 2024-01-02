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
my_agents=[
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0",
"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1.1 Safari/605.1.15",
"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
"Mozilla/5.0 (iPhone; CPU iPhone OS 11_4 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15E148 Safari/604.1"
]

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
}
def good_match(s1, s2):
    set1 = set(s1)
    set2 = set(s2)
    common_chars = set1.intersection(set2)
    if len(common_chars)*1.0  / (len(set2) + 0.1) > 0.6:
       return True 
    return False

BASE_URL="https://www.tbsdy.com/"
def movie_page(movie_url):
    session = requests.Session()
    headers['User-Agent'] = random.choice(my_agents)
    resp = session.get(movie_url, headers = headers)  ##  此处输入的url是登录后的豆瓣网页链接
    httpDoc = resp.text
    
    soup = None
    try:
        soup = BeautifulSoup(httpDoc, 'html5lib')
    except:
        soup = BeautifulSoup(httpDoc, 'html.parser')
    htmlNode = soup.html
    headNode = htmlNode.head
    bodyNode = htmlNode.body
    urls = []
    try:
        video_download_link_info = bodyNode.find("div", attrs={"class":"video_download_link_info"})
        items = video_download_link_info.find_all("div", attrs={"class":"video_download_link_item"})
        for item in items:
            video_download_link_name = item.find("div", attrs={"class":"video_download_link_name"})
            video_link_node = video_download_link_name.find("div")
            if video_link_node.has_attr("href"):
                urls.append(video_link_node["href"])
    except:
        print("error********", traceback.format_exc(), movie_url)
    return urls

def get_tbs_movie(movie_name):
    rets = []
    try:
        req_url="https://www.tbsdy.com/search.html?keyword={}".format(movie_name)
        session = requests.Session()
        headers['User-Agent'] = random.choice(my_agents)
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
        try:
            search_result_list = bodyNode.find('div', attrs={"class":"search_result_list"})
            search_result_items = search_result_list.find_all("div", attrs={"class":"search_result_item"})
            for search_item in search_result_items:
                search_result_title = search_item.find("a", attrs={"class":"search_result_title"}) 
                url = BASE_URL+search_result_title["href"]
                title = search_result_title.text.strip()
                search_issue_date = search_item.find("span", attrs={"class":"search_result_issue_date"})
                date=""
                if search_issue_date is not None:
                    date = search_issue_date.text.strip()
                label_node = search_item.find("div", attrs={"class":"video_labels"})
                labels = [] 
                if label_node is not None:
                    video_spans = label_node.find_all("span")
                    for video_span in video_spans:
                        labels.append(video_span.text.strip())
                if "video" not in url or not good_match(title, movie_name):
                    continue
                movie_urls = movie_page(url)
                if len(movie_urls) > 0:
                    rets.append("{}{} {}\n{}".format(title, date, ",".join(labels), "\n".join(movie_urls[0:5])))
                if len(rets) > 5:
                    break
        except:
            print("*(***&^*&^*", traceback.format_exc())
    except:
        print("**&^*&^*", traceback.format_exc())
    if len(rets) > 0:
        rets.insert(0, "如果打不开，请复制链接到浏览器观看, 不要相信视频里的广告!!!\n")
    return rets
print(get_tbs_movie("旺卡"))
