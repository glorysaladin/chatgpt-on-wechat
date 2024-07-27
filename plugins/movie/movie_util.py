# -*- coding: utf-8 -*-
import sys, re, os, time, json, re
from datetime import datetime
import html5lib
from bs4 import BeautifulSoup
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
        i = 0
        httpDoc=""
        while i < 3:
            try:
                resp = requests.get(url, headers=headers, proxies=proxies, timeout=10)
                httpDoc = resp.text
                resp.close()
                break
            except:
                i+=1

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
        rets.append("👉资源可以从群公告取")
        #rets.append("https://6url.cn/tEQs9z")
    
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
        #print(f"start affdz {web_url} {moviename}")
        url="{}/search.php?q={}".format(web_url, moviename)
        proxies = {"http":None, "https":None}
        i = 0 
        httpDoc=""
        while i < 3:
            print(f"try {i} times.")
            try:
                resp = requests.get(url, headers=headers, proxies=proxies, timeout=(10,10))
                httpDoc = resp.text
                resp.close()
                break
            except requests.exceptions.RequestException as e:
                i+=1
                print("get from affdz error", e)

        soup = None
        #print(f"start affdz2 {web_url} {moviename}")
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
    #print(f"start affdz3 {web_url} {moviename}")
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
        if len(rets) == 0:
            rets.extend(get_from_uukk(moviename, is_pay_user))
            if len(rets) > 0:
                source += "2"

        if len(rets) == 0:
            rets.extend(get_from_funletu(moviename))
            if len(rets) > 0:
                source += "3"

    if len(rets) == 0:
        return False, ["未找到资源, 可尝试缩短关键词, 只保留资源名, 不要带'第几部第几集谢谢'，等无关词."]

    num = len(rets)
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
    print(update_movies)
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
        msg_ret.append("资源链接可以从群公告获取")
        #msg_ret.append("https://6url.cn/tEQs9z")
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
#movie_update_data={'你好星期六': '5.26', '声生不息家年华': '02.18', '与恶魔有约': '16集', '我们的美好生活': '1.20', '爱的修学旅行': '02.07', '花儿与少年': '02.07', '天官赐福2': '12集', '我可以47': '12.27', '请和我的老公结婚': '16集', '你也有今天': '36集', '宋慈韶华录': '25集', '我们的翻译官': '36集', '大江大河之岁月如歌': '33集', '黑土无言': '12', '如果奔跑是我的人生': '28集', '19层': '30集', '名侦探学院': '02.17', '遮天': '59集', '祈今朝': '36集', '仙剑四': '36集', '要久久爱': '32集', '小城故事多': '30集', '杀人者的购物中心': '08集', '乌有之地': '1.26', '好久没做': '06集', '狗剩快跑': '24集', '空战群英': '08集', '大王饶命': '12集', '吞噬星空': '121集', '赵本山小品合集': '2.11', '欢乐喜剧人小品合集': '1.28', '黄宏、潘长江小品合集': '1.28', '冯巩、郭冬临相声小品合集': '1.28', '赵丽蓉小品合集': '1.28', '陈佩斯、朱时茂小品合集': '1.28', '郭德纲相声': '1.28', '春节联欢晚会相声小品合集': '1.28', '历年春晚小品相声合集216集': '2.11', '50部春晚小品大全': '2.11', '金瓶梅原著【全彩插图】【未删减】': '1.28', '800本连环画儿时记忆3': '1.28', '800本连环画儿时记忆2': '1.28', '800本连环画儿时记忆1': '1.28', '四大名著 连环画': '1.28', '金庸小说漫画': '1.28', '伊藤润二合集': '1.28', '聊斋故事连环画': '1.28', '高清怀旧连环画': '1.28', '金瓶梅（全彩连环画版）绝版彩色国画经典珍藏': '1.28', '网易云评论最多的中文歌曲TOP50': '1.28', '网易云评论最多的粤语歌曲TOP100': '1.28', '网易云评论最多的英文TOP100': '1.28', '网易云评论最多的日语TOP100': '1.28', '网易云评论最多的韩语歌曲TOP200': '1.28', '网易云评论最多的纯音乐TOP100': '1.28', '全网顶级AI绘画极品美女': '1.28', '19x电影合集70部': '1.28', '豆瓣评分Top20': '1.28', '韩国最出色的R限制【合集】': '1.28', '影迷投票选出了近十年他们最喜欢的50部恐怖片！': '1.28', '人人影视电影合集--高清双语字幕（珍藏版）': '1.28', '宫崎骏作品合集': '1.28', '皮克斯动画合集': '1.28', '经典香港电影合集（修复未删减版本）': '1.28', '迪士尼系列动画139部蓝光珍藏版': '1.28', '周星驰系列': '1.28', 'DC电影宇宙系列': '1.28', '漫威电影宇宙(MCU)系列': '1.28', '一百年一百部 美国电影学院百年百部影片': '1.28', '2023奥斯卡提名电影合集(95届)': '1.28', '奥斯卡获奖影片1988-2022': '1.28', '豆瓣电影Top250': '1.28', '欢乐家长群': '40集', '阿麦从军': '36集', '暴雪时分': '06集', '在暴雪时分': '30集', '尘封十三载': '24集', '授她以柄': '20集', '少爷和我': '12集', '斗破苍穹年番': '95集', '独一无二的她': '24 集', '2024湖南卫视春节联欢晚会': '2.5', '同心向未来·2024中国网络视听年度盛典': '2.5', '世界各地的性与爱  (2018) 中文字幕': '2.5', '台湾食堂三季': '2.5', '世界各地的性与爱': '2.5', '大唐狄公案': '32集', '南来北往': '39集', '黑白潜行': '2.7', '爱爱内含光(台剧)': '8集', '甜甜的陷阱': '24集', '历届春晚小品相声': '2.11', '仙逆': '38集', '飞驰人生': '2.13', '如懿传': '87集', '烟火人间': '18集', 'xianh\u2006xun\u2006ai\u2006qing': 'None', '乡村爱情16': '40集', '动物园里有什么': '2.16', '缉恶': '2.16', '大侦探第九季': '5.08', '全员加速中': '4.18', '烟火人家': '41集', '金手指': '2.2', '大理寺少卿游': '36集', '春日浓情  14集': 'None', '师兄啊师兄 24集': 'None', '冰火魔厨': '138集', '春日浓情': '17集', '师兄啊师兄': '26集', '猎冰': '18集', '大理寺少卿': '12集', '南来北往2': '39集', '怒潮': '2.22', '种地吧第二季': '2.23', '暮色心迹': '24集', '明星大侦探第九季': '3.02', '炙爱之战': '2.14', '猎冰2': '09集', '行尸走肉：存活之人': '06集', '我想和你唱第5季': '2.24', '你的岛屿已抵达': '12集', '犯罪现场4': '10集', '房东在上': '98集', '大王别慌张': '14集', '大主宰': '50集', '半熟恋人3': '5.02', '无限超越班2': '5.11', '乐可广播剧': '2.28', '婚后事': '14集', '江河日上': '24集', '幕府将军': '10集', '唐人街探案2剧版': '03集', '光环第二季': '07集', '东京罪恶2': '05集', '周处除三害': '3.1', '金字塔游戏': '06集', '大理寺 少卿游': '22', '飞驰人生热爱篇': '10集', '别对我动心': '18集', '唐人街探案2': '16集', '种地吧2024': '4.28', '葬送的芙莉莲': '28集', '仙武帝尊': '78集', '永安梦': '24集', '破墓': '4.23', '近战法师': '20集', '紫川·光明三杰': '24集', '一梦浮生': '22集', '眼泪女王': '16集', '潜行 刘德华 2023': '3.14', '烈焰': '40集', '宣武门': '41集', '今晚开放麦第2季': '3.13', '花间令': '32集', '谢谢你温暖我': '15集', '与凤行': '39集', '小日子': '27集', '执笔': '24集', '追风者': '38集', '欢乐颂5': '34集', '遥不可及的爱': '3.36', '乘风踏浪': '2024集', '今天的她们': '24集', '百炼成神': '78集', '步步倾心': '28集', '猜猜我是谁': '24集', '我独自升级': '12集', '惜花芷': '2024', '不够善良的我们': '08集', '红衣醉': '26集', '盒子里的猫': '5.26', '手术直播间': '28集', '海贼王': '1103集', '诛仙2024': '37集', '哈哈哈哈哈4': '5.26', '小谢尔顿第7季': '06集', '又见逍遥': '40集', '难寻': '28集', '恋爱兄妹': '16集', '公寓404': '08集', '七人的复活': '16集', '美好世界': '14集', '逆天奇案2': '30集', '承欢记': '2024', '城中之城': '40集', '春色寄情人': '21集', '背着善宰跑': '16集', '西行纪5': '36集', '西行纪合集': '4.26', '鉴罪女法医之魇始': '24集', '爱在天摇地': '24集', '爱在天摇地动时': '24集', '种地吧2': '5.25', '情靡': '92集', '炼气3000层开局收女帝为徒': '78集', '微暗之火': '28集', '我什么时候无敌了': '94集', '亲爱的宋小姐': '69集', '乌龙孕事': '76集', '游子归家': '88集', '总裁夫人为何那样': '79集', '新生': '10集', '我的阿勒泰': '08集', '此刻无声': '20集', '哈尔滨一九四四': '40集', '不可告人': '1080', '庆余年第二季': '31集', '家族荣耀之继承者': '1080'}
#print(send_update_to_group(movie_update_data, "https://moviespace02.com", True))
#print(send_update_to_group(movie_update_data, "https://affdz.com"))
#print(get_latest_postid(1500, "https://affdz.com"))
#print(movie_update_data)
#print(search_movie(["https://moviespace02.com", "https://moviespace01.com"], "仙逆", True, False, False))
#print(search_movie(["https://moviespace02.com", "https://moviespace01.com"], "莲花楼", True, False, False))
#print(get_latest_postid(1, "https://moviespace02.com"))
#if __name__ == "__main__":
#    print(search_movie("https://affdz.com", "天官赐福第二季"))
