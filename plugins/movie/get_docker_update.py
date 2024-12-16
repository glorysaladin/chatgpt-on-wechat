import sys,os,re
from datetime import datetime
import subprocess
from movie_util import *

from dateutil import parser
from datetime import timedelta

def parse_time(text):
    pattern = r"\[(\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]"
    match = re.search(pattern, text)
    if match:
        # 提取并打印时间
        time_extracted = match.group(1)
        return time_extracted
    else:
        print("未找到匹配的时间格式")
def parse_time2(text):
    items = text.strip().split(" ")

    # 给定的UTC时间戳
    try:
        utc_timestamp = items[0]
        print(utc_timestamp)
        
        # 解析UTC时间戳
        utc_time = parser.parse(utc_timestamp)
        
        # 将UTC时间转换为东八区时间（UTC+8）
        beijing_time = utc_time + timedelta(hours=8)
        
        # 格式化输出为所需的格式
        formatted_time = beijing_time.strftime('%Y-%m-%d %H:%M:%S')
        print(formatted_time)
    except:
        return ""
    
    return formatted_time

def comp_time(timestamp1, timestamp2):
    if len(timestamp2) == 0:
        return 1
    # 将字符串转换为datetime对象
    time1 = datetime.strptime(timestamp1, "%Y-%m-%d %H:%M:%S")
    time2 = datetime.strptime(timestamp2, "%Y-%m-%d %H:%M:%S")
     
    # 比较时间戳
    if time1 < time2:
        return -1
    elif time1 > time2:
        return 1
    else:
        return 0

def load_last_push_time(inp):
    if not os.path.isfile(inp):
        return ""
    f = open(inp,"r")
    line = f.readline()
    return line.strip()

def parse_movie_name(text):
    # 使用正则表达式匹配书名号内的文本
    match = re.search(r'《(.*?)》', text)
     
    # 如果找到了匹配项，则提取并打印书名
    if match:
        movie_name= match.group(1)
        #print("提取的书名是：", movie_name)
        return movie_name
    else:
        print("未找到书名号内的文本。")
    return ""

def parse_movie_series(text):
    match = re.search('🎞️(.*)', text)

    if match:
        extracted_text = match.group(1)
        #print("提取的文本是：", extracted_text)
        return extracted_text 
    else:
        print("未找到匹配的文本。")
    return ""

def parse_cancel_movie(info_lines):
    if len(info_lines) ==0:
        return []
    rets = []
    for info in info_lines:
        cur_movie_name = parse_movie_name(info)
        rets.append(cur_movie_name)
    return rets

def parse_update_movie(info_lines, web_url):
    if len(info_lines) == 0:
        return []
    #print(info_lines)
    cur_start_found = False
    updates = []
    movie_info = {}
    cur_movie_name = ""
    for info in info_lines:
        if "添加追更" in info:
            if len(updates) > 0 and len(cur_movie_name) > 0:
                movie_info[cur_movie_name] = updates
                cur_movie_name = ""
                updates = []
            cur_start_found = True
            cur_movie_name = parse_movie_name(info)
            movie_info[cur_movie_name] = []
            continue
        if cur_start_found:
            if "🎞️" in info:
                series = parse_movie_series(info)
                updates.append(" -- " + series)
    if len(updates) > 0 and len(cur_movie_name) > 0:
        movie_info[cur_movie_name] = updates

    print("movie_info=", movie_info)
    final_rets = []
    for movie_name in movie_info:
        tmp_rets = []
        rets = get_from_affdz(web_url, movie_name, True)
        link = ""
        for ret in rets:
            items = ret.split("\n")
            if len(items) == 2:
                link = items[1]
                break
        if link != "":
            tmp_rets.append("🎬 [{}] 有更新".format(movie_name))
            tmp_rets.append("\n".join(movie_info[movie_name]))
            tmp_rets.append(link)
        if len(tmp_rets) > 0:
            final_rets.extend(tmp_rets)
            final_rets.append("\n")
    print("final_rets=",final_rets)
    return final_rets

    #if len(movie_info) > 0:
    #    fo = open(update_history, "w")
    #    fo.write(json.dumps(movie_info))
    #    fo.close()
    #return movie_info

def get_auto_update(web_url, docker_image_name):
    curdir=os.path.dirname(os.path.abspath(__file__))
    shell_cmd =  "sh {}/get_docker_log.sh {}".format(curdir, docker_image_name)
    return_cmd = subprocess.run(shell_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8',shell=True)
    movie_source_map = {}
    if return_cmd.returncode != 0:
        return ""
    ret_val = return_cmd.stdout
    lines = ret_val.split("\n")

    config_log = "{}/quark_update_config.txt".format(curdir)
    
    LAST_PUSH_TIME = load_last_push_time(config_log)
    start_found=False
    push_info_lines = []
    CUR_PUSH_TIME = ""
    rets = []
    for line in lines:
        if "程序结束" in line:
            # 处理中间数据
            cur_update_info = parse_update_movie(push_info_lines, web_url)
            rets.extend(cur_update_info)
            start_found = False
            push_info_lines = []

        if start_found:
            push_info_lines.append(line)
    
        if "推送通知" in line:
            push_time = parse_time2(line)
            if push_time == "":
                continue
            CUR_PUSH_TIME = push_time
            if comp_time(CUR_PUSH_TIME, LAST_PUSH_TIME) == 1:
                #有更新
                start_found = True
    
    if CUR_PUSH_TIME != "":
       fo = open(config_log, "w")
       fo.write(CUR_PUSH_TIME)
       fo.close()
    if len(rets) > 0:
        return "\n".join(rets)
    return ""

def get_update_cancel(docker_image_name, url):
    curdir=os.path.dirname(os.path.abspath(__file__))
    shell_cmd =  "sh {}/get_docker_log.sh {}".format(curdir, docker_image_name)
    return_cmd = subprocess.run(shell_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8',shell=True)
    movie_source_map = {}
    if return_cmd.returncode != 0:
        return ""
    ret_val = return_cmd.stdout
    lines = ret_val.split("\n")

    config_log = "{}/quark_cancel_config.txt".format(curdir)
    
    LAST_CHECK_TIME = load_last_push_time(config_log)
    start_found=False
    push_info_lines = []
    CUR_CHECK_TIME = ""
    rets = []
    for line in lines:
        if "好友已取消了分享" in line or "文件涉及违规内容" in line or "分享地址已失效" in line:
            push_time = parse_time2(line)
            if push_time == "":
                continue
            CUR_CHECK_TIME = push_time
            if comp_time(CUR_CHECK_TIME, LAST_CHECK_TIME) == 1:
                push_info_lines.append(line)

    # 处理中间数据
    rets = parse_cancel_movie(push_info_lines)

    if CUR_CHECK_TIME != "":
       fo = open(config_log, "w")
       fo.write(CUR_CHECK_TIME)
       fo.close()

    if len(rets) > 0:
        rets = list(set(rets))
        return "分享链接需要修改: \n{}\n{}".format("\n".join(rets), url)
    return ""

#if __name__ == "__main__":
#    print("get_auto_update=", get_auto_update("https://www.affdz.com", "quark-auto-save-qian"))
#    print("get_update_cancel=", get_update_cancel("quark-auto-save-qian", "http://8.141.94.24:5006/"))
