# -*- coding: utf-8 -*-
import sys, re, os, time, json
import html5lib
from bs4 import BeautifulSoup
import logging
import logging.handlers
import traceback
import urllib
import requests
from .get_pan_from_qianfan import *
from .get_pan_from_funletu import *
from .get_pan_from_uukk import *

def download(url):
    resp = requests.get(url)
    return resp.text

def _extract_update(httpDoc, pattern='json'):
    soup = None
    try:
        soup = BeautifulSoup(httpDoc, 'html5lib')
    except:
        soup = BeautifulSoup(httpDoc, 'html.parser')
    htmlNode = soup.html
    headNode = htmlNode.head
    bodyNode = htmlNode.body
    itemNodes = bodyNode.find_all(attrs={"class": "sou-con"})
    rets = {}
    for item in itemNodes:
        divNodes = item.find_all(attrs={"class":"sou-con-title"})
        hit=False
        for div in divNodes:
            if "持续更新" in div.text:
                hit = True
                break
        if hit:
            aNodes = item.find_all('a')
            for item in aNodes:
                if item.has_key("title") and item.has_key('href'):
                     href = item['href']
                     title = item['title']
                     if "post" not in href:
                         continue
                     rets[title]=href
    return rets


def _extract_movie_info(httpDoc, pattern='json'):
    soup = None
    try:
        soup = BeautifulSoup(httpDoc, 'html5lib')
    except:
        soup = BeautifulSoup(httpDoc, 'html.parser')
    htmlNode = soup.html
    bodyNode = htmlNode.body
    itemNodes = bodyNode.find_all('a')
    title_postid_map = {}
    for item in itemNodes:
        if item.has_key("title") and item.has_key('href'):
            href = item['href']
            title = item['title']
            if "post" not in href:
                continue
            title_postid_map[title] = href
    return title_postid_map

def get_source_link(url):
    resp = requests.get(url)
    httpDoc = resp.text
    soup = None
    try:
        soup = BeautifulSoup(httpDoc, 'html5lib')
    except:
        soup = BeautifulSoup(httpDoc, 'html.parser')
    htmlNode = soup.html
    headNode = htmlNode.head
    bodyNode = htmlNode.body
    itemNodes = bodyNode.find_all(attrs={"class": "sou-con"})
    contentNode = bodyNode.find('div', attrs={"class":"article-content"})
    sourceLinks = contentNode.find_all('a')
    for link in sourceLinks:
        if "http" in link["href"]:
            return link["href"]
    return ""

def get_movie_update(last_post_id):
    rets = {}
    urls = ["https://affdz.com", "https://affdz.com/page_2.html"]
    for url in urls:
        html_page=download(url)
        ret_page=_extract_movie_info(html_page)
        rets.update(ret_page)

    max_post_id = -1
    movie_list = []
    for key in rets:
        href = rets[key]
        cur_id = int(href.split("/")[-1].split(".")[0])
        #print(key, href, cur_id)
        if cur_id > max_post_id:
            max_post_id = cur_id
        if cur_id > last_post_id:
            movie_list.append(key)
    print("1", movie_list)

    html = download("https://affdz.com/tags-1.html")
    update_rets = _extract_update(html)
    for title in update_rets:
        movie_list.append(title)
    print("2", movie_list)

    rets.update(update_rets)
    #print(rets, max_post_id, last_post_id)

    #movie_list = list(set(movie_list))
    message_list =[]
    prefix = "【今日影视资源更新】"
    message_list.append(prefix)

    idx = 0
    exist_map={}
    for movie in movie_list:
        if movie in exist_map:
            continue
        exist_map[movie]=1
        link = ""
        if movie in rets:
            link = get_source_link(rets[movie])
            if link == "":
                link = rets[movie]
        message_list.append("{}: {}\n链接: {}".format(idx, movie, link))
        idx += 1

    message_list.append("全部资源链接:\n https://sourl.cn/XeN2ex\n夸克网盘SVIP会员(12元)\nhttps://sourl.cn/vAxErZ \n联系群主.")

    if len(movie_list) == 0:
        print("no update film.")
        sys.exit()

    message = "\n".join(message_list)
    return (max_post_id, message)

def good_match(s1, s2):
    set1 = set(s1)
    set2 = set(s2)
    common_chars = set1.intersection(set2)
    if len(common_chars)*1.0  / (len(set1) + 0.1) > 0.2:
       return True 
    return False

def _get_search_result(httpDoc, moviename, pattern='json'):
    soup = None
    try:
        soup = BeautifulSoup(httpDoc, 'html5lib')
    except:
        soup = BeautifulSoup(httpDoc, 'html.parser')
    htmlNode = soup.html
    bodyNode = htmlNode.body
    listNode = bodyNode.find('div', attrs={"class":"sou-con-list"})
    aNodes = listNode.find_all('a')
    rets = []
    source=""
    for item in aNodes:
        href = ""
        title = ""
        if item.has_key("title") and item.has_key('href'):
             href = item['href']
             title = item['title'].replace("<strong>", "").replace("</strong>", "")
        if good_match(moviename, title):
             movieurl = href
             link = get_source_link(href)
             if link.strip() == "":
                 link = href.split("url=")[1].split("&")[0]
             rets.append("{}\n{}".format(title, link))
             source="1"

    if len(rets) == 0:
        rets = get_from_funletu(moviename)
        if len(rets) > 0:
            source += "2"

    if len(rets) == 0:
        rets = get_from_uukk(moviename)
        if len(rets) > 0:
            source += "3"

    if len(rets) == 0:
        rets = get_from_qianfan(moviename)
        if len(rets) > 0:
            source += "4"
        if len(rets) == 0:
            return False, "未找到资源, 可尝试缩短关键词, 只保留资源名."
    if len(rets) >= 5:
       num = len(rets)
       rets = rets[0:5]
       rets.insert(0, "[{}]找到 {} 个资源, 展示前5个:\n".format(source, num))

    if len(rets) < 5:
       rets.insert(0, "[{}]找到 {} 个资源:\n".format(source, len(rets)))
    return True, "\n".join(rets)

def search_movie(web_url, movie):
    url="{}/search.php?q={}".format(web_url, movie)
    resp = requests.get(url)
    return _get_search_result(resp.text, movie)

#print(get_movie_update(1414))
#if __name__ == "__main__":
#    print(search_movie("https://affdz.com", "天官赐福第二季"))
