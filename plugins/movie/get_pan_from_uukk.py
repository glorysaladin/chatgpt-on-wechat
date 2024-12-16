# -*- coding: utf-8 -*-
import subprocess, json, os
import traceback

def good_match(s1, s2):
    set1 = set(s1)
    set2 = set(s2)
    common_chars = set1.intersection(set2)
    if len(common_chars)*1.0  / (len(set1) + 0.1) > 0.6:
       return True 
    return False

COOKIE="Hm_lvt_cce07f87930c14786d9eced9c08d0e89=1714149361,1715772698; Hm_lvt_0f5b4479829961ae8a3cb0e80ec93808=1720437132,1720530560,1720695559,1720963126; __51cke__=; __tins__21897559=%7B%22sid%22%3A%201721580186807%2C%20%22vd%22%3A%203%2C%20%22expires%22%3A%201721582100028%7D; __51laig__=19"
#URLS=["http://22006.cn/v/api/getJuzi", "http://22006.cn/v/api/getDyfx", "http://22006.cn/v/api/getTTZJB"]
#URLS=["http://uukk6.cn/v/api/getJuzi", "http://uukk6.cn/v/api/getDyfx", "http://uukk6.cn/v/api/getTTZJB"]
URLS=["http://www.kkkob.com/v/api/search", "http://www.kkkob.com/v/api/getDJ","http://www.kkkob.com/v/api/getJuzi","http://www.kkkob.com/v/api/getXiaoyu"]

def get_from_uukk(query, is_pay_user):
    rets = []
    for URL in URLS:
        if not is_pay_user and len(rets) > 0:
            break
        rets.extend(search(query, URL))
    print("uukk_rets=", rets)
    return rets

def search(query, url):
    rets =[]
    try:
        curdir = os.path.dirname(os.path.abspath(__file__))
        shell_cmd =  "sh {}/curl_uukk.sh {} {} \"{}\"".format(curdir, query, url, COOKIE)
        return_cmd = subprocess.run(shell_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8',shell=True)
        if return_cmd.returncode == 0:
            ret_val = return_cmd.stdout
            js = {}
            try:
                js = json.loads(ret_val)
            except:
                print("ret_val=", ret_val)
                print(traceback.format_exc())

            for item in js["list"]:
                question=item['question']
                answer=item["answer"]
                if "失效" in question:
                    continue
                answer = answer.replace(question, "")
                answer = answer.replace("\n链接：", "\n")
                answer = answer.replace("链接：", "\n")
                answer = answer.replace("链接:", "\n")
                if good_match(query, question):
                    tmp="{}\n{}".format(question, answer)
                    tmp = tmp.replace("\n\n", "\n")
                    rets.append(tmp)
        print("*********{}\n{}\n\n".format(url , rets))
    except:
        print(traceback.format_exc())
    return rets

#print(get_from_uukk("庆余年", True))
