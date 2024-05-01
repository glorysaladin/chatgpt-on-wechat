# -*- coding: utf-8 -*-
import sys, re, os, time, json, re
from datetime import datetime
import html5lib
from bs4 import BeautifulSoup
import logging
import logging.handlers
import traceback
import urllib
import requests
import random
os.environ['NO_PROXY'] = 'affdz.com,moviespace01.com,moviespace02.com'

cur_dir=os.path.dirname(__file__)
sys.path.append(cur_dir)

from get_pan_from_funletu import *
from get_pan_from_uukk import *
from get_movie_from_soupian import *
from get_movie_from_zhuiyingmao import *

headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.41"}

def download(url):
    proxies = {"http":None, "https":None}
    resp = requests.get(url, headers=headers, proxies=proxies)
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
    title_text = ""
    try:
        proxies = {"http":None, "https":None}
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=3)
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
        titleNode = bodyNode.find('h1', attrs={"class": "detail_title"})
        if titleNode is not None:
            title_text = titleNode.text

        contentNode = bodyNode.find('div', attrs={"class":"article-content"})
        sourceLinks = contentNode.find_all('a')
        for link in sourceLinks:
            if "http" in link["href"]:
                return link["href"], title_text
    except:
        print(traceback.format_exc())
    return "", title_text

def get_latest_postid(last_post_id, web_url):
    rets = {}
    html_page=download(web_url)
    ret_page=_extract_movie_info(html_page)
    rets.update(ret_page)

    max_post_id = -1
    for key in rets:
        href = rets[key]
        cur_id = int(href.split("/")[-1].split(".")[0])
        if cur_id > max_post_id:
            max_post_id = cur_id
    return max_post_id

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
            link, title_text = get_source_link(rets[movie])
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

def get_random_movie(start_post, end_post, rand_num, base_url, show_link=False):
    rets = []
    for post_id in random.sample(range(start_post, end_post), rand_num):
        url="{}/post/{}.html".format(base_url, post_id)
        link, title = get_source_link(url) 
        if link != "":
            if not show_link:
                link = ""
            rets.append("{}\n{}".format(title, link)) 
    if not show_link and len(rets) > 0:
        rets.append("👉资源可以从群公告的网站获取")
    
    return "\n".join(rets) 

def good_match(s1, s2):
    set1 = set(s1)
    set2 = set(s2)
    common_chars = set1.intersection(set2)
    if len(common_chars)*1.0  / (len(set1) + 0.1) > 0.2:
       return True 
    return False

def get_from_affdz(web_url, moviename, show_link=False):
    rets = []
    try:
        url="{}/search.php?q={}".format(web_url, moviename)
        proxies = {"http":None, "https":None}
        resp = requests.get(url, headers=headers, proxies=proxies)
        httpDoc = resp.text
        soup = None
        try:
            soup = BeautifulSoup(httpDoc, 'html5lib')
        except:
            soup = BeautifulSoup(httpDoc, 'html.parser')
        htmlNode = soup.html
        bodyNode = htmlNode.body
        listNode = bodyNode.find('div', attrs={"class":"sou-con-list"})
        aNodes = listNode.find_all('a')
        source=""
        for item in aNodes:
            href = ""
            title = ""
            if item.has_attr("title") and item.has_attr('href'):
                 href = item['href']
                 if "post" not in href:
                     continue
                 title = item['title'].replace("<strong>", "").replace("</strong>", "")
            if good_match(moviename, title):
                 movieurl = href
                 link, title_text = get_source_link(href)
                 if link.strip() == "":
                     link = href.split("url=")[1].split("&")[0]
                 if not show_link:
                     link = " "
                 rets.append("{}\n{}".format(title, link))
    except:
        print("error=",traceback.format_exc())
    return rets

def _get_search_result(web_url_list, moviename, show_link, is_pay_user, only_affdz, pattern='json'):
    source = ''
    rets = []
    for idx, web_url in enumerate(web_url_list):
        rets.extend(get_from_affdz(web_url, moviename, show_link))
        if len(rets) > 0:
            source = source + str(idx)
            break

    if not only_affdz:
        if len(rets) == 0 or is_pay_user :
            rets.extend(get_from_funletu(moviename))
            if len(rets) > 0:
                source += "2"

        if len(rets) == 0 or is_pay_user:
            rets.extend(get_from_uukk(moviename, is_pay_user))
            if len(rets) > 0:
                source += "3"

    if len(rets) == 0:
        return False, ["未找到资源, 可尝试缩短关键词, 只保留资源名, 不要带'第几部第几集谢谢'，等无关词."]

    num = len(rets)
    if not is_pay_user:
       rets = rets[0:5]
    else:
       rets = rets[0:20]
    rets.insert(0, "[{}]找到 {} 个相关资源:\n".format(source, num))

    return True, rets

def search_movie(web_url_list, movie, show_link=False, is_pay_user=False, only_affdz=False):
    return _get_search_result(web_url_list, movie, show_link, is_pay_user, only_affdz)

def need_update(my_count, other_count):
    try:
        if "." in my_count and "." in other_count:
            # 将日期字符串转换为datetime对象
            date1_obj = datetime.strptime(str(my_count), "%m.%d")
            date2_obj = datetime.strptime(str(other_count), "%m.%d")
            if date1_obj < date2_obj:
                return True
            return False
        else:
            if "." not in my_count and "." not in other_count:
                if int(other_count) > 2000:
                    return False
                if int(my_count) < int(other_count):
                    return True
                return False
    except:
        pass
    return False

def send_update_to_group(movie_update_data, web_url, show_link):
    curdir=os.path.dirname(os.path.abspath(__file__))
    shell_cmd =  "sh {}/get_state_from_feishu.sh".format(curdir)
    return_cmd = subprocess.run(shell_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8',shell=True)
    update_movies = []
    movie_source_map = {}
    if return_cmd.returncode == 0:
        ret_val = return_cmd.stdout
        js = json.loads(ret_val)
        values = js.get("data", {}).get("valueRange", {}).get("values", [])
        for item in values:
            if item[0] is not None and item[0] != "None" and item[0] != "null":
                movie_name = item[0].strip()
                version = str(item[1]).strip()
                if item[2] is not None:
                    source = item[2].strip() 
                    movie_source_map[movie_name] = source
                if movie_name not in movie_update_data or movie_update_data[movie_name] is None or movie_update_data[movie_name] == "None":
                    movie_update_data[movie_name] = version
                    update_movies.append(movie_name)
                else:
                    cur_version = version.replace("集", "")
                    last_version = movie_update_data[movie_name].replace("集", "")
                    if need_update(last_version, cur_version):
                        update_movies.append(movie_name)
                        movie_update_data[movie_name] = version
    msg_ret = []
    for movie in update_movies:
        link = ""
        if movie in movie_source_map and "http" in movie_source_map[movie]:
            link = movie_source_map[movie] 
        else:
            ret = get_from_affdz(web_url, movie, True)
            if len(ret) > 0:
                items = ret[0].split("\n")
                link = items[1]
        if len(link) > 0:
            if not show_link:
                link = ""
            msg = "[{}] (更新到{})\n{}".format(movie, movie_update_data[movie], link)
            msg_ret.append(msg)
    print("update movies={}".format(msg_ret))
    if not show_link and len(msg_ret) > 0:
        msg_ret.append("资源链接可以从群公告的网站里找一下")
    return "\n\n".join(msg_ret)
 
def check_update():
    update_infos=[]
    curdir=os.path.dirname(os.path.abspath(__file__))
    shell_cmd =  "sh {}/get_state_from_feishu.sh".format(curdir)
    return_cmd = subprocess.run(shell_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8',shell=True)
    movie_series =[]
    if return_cmd.returncode == 0:
        ret_val = return_cmd.stdout
        js = json.loads(ret_val)
        values = js.get("data", {}).get("valueRange", {}).get("values", [])
        for item in values:
            if item[3] is not None:
                continue
            if item[0] is not None:
                movie_series.append((item[0], str(item[1]).replace("集", ""), item[2]))
    print("movie_series={}".format(movie_series))
    for moviename, my_count, source in movie_series:
        rets = []
        fuletu_rets = get_from_funletu(moviename)
        #print("query=", moviename, "fuletu_rets=", fuletu_rets)
        rets.extend(fuletu_rets)
        uukk_rets = get_from_uukk(moviename, True)
        rets.extend(uukk_rets)
        for ret in rets:
            #print(ret)
            try:
                if "quark" not in ret:
                    continue
                items = ret.strip().split("\n")
                if len(items) >= 2:
                    cur_name = items[0]
                    pattern = r"[更|全]\D*(\d+\.?\d*)"
                    matches = re.findall(pattern, cur_name)
                    for match in matches:
                        if need_update(my_count, match):
                            update_infos.append("【{}】{}\n当前 （{}）--> 最新 （{}）\n{}\n".format(moviename, source, my_count, match, ret))
            except:
                print("error", ret)
    return "\n".join(update_infos)

#print(check_update())
#print(get_movie_update(1414))
#print(get_source_link("https://moviespace01.com/post/1671.html"))
#print(get_random_movie(1000, 1500, 2,"https://affdz.com"))

#movie_version="/home/lighthouse/project/chatgpt-on-wechat2/plugins/movie/movie_update_version.pkl"
#movie_update_data={}
#print(send_update_to_group(movie_update_data, "https://moviespace02.com", True))
#print(movie_update_data)
#print(search_movie(["https://moviespace02.com"], "大侦探", True, False, True))
#print(get_latest_postid(1, "https://moviespace02.com"))
#if __name__ == "__main__":
#    print(search_movie("https://affdz.com", "天官赐福第二季"))
