# -*- coding: utf-8 -*-
import sys, re, os, time, json
import html5lib
from bs4 import BeautifulSoup
import logging
import logging.handlers
import traceback
import urllib
import requests

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

    message_list.append("【群福利】\n夸克网盘SVIP会员(12元)\nhttps://sourl.cn/vAxErZ \n联系群主.")

    if len(movie_list) == 0:
        print("no update film.")
        sys.exit()

    message = "\n".join(message_list)
    return (max_post_id, message)
#print(get_movie_update(1414))
