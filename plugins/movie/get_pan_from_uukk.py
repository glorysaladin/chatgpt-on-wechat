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

COOKIE="Hm_lvt_cce07f87930c14786d9eced9c08d0e89=1700320320,1700750079,1701444675; Hm_lpvt_cce07f87930c14786d9eced9c08d0e89=1701964941"
#URLS=["http://uukk6.cn/v/api/getJuzi", "http://uukk6.cn/v/api/getDyfx", "http://uukk6.cn/v/api/getTTZJB"]
#URLS=["http://uukk6.cn/v/api/getJuzi", "http://uukk6.cn/v/api/getTTZJB"]
#URLS=["http://22006.cn/v/api/getJuzi", "http://22006.cn/v/api/getpwdcfg", "http://22006.cn/v/api/getDyfx", "http://22006.cn/v/api/getTTZJB"]
URLS=["http://22006.cn/v/api/getJuzi", "http://22006.cn/v/api/getDyfx", "http://22006.cn/v/api/getTTZJB"]

def get_from_uukk(query, is_pay_user):
    rets = []
    for URL in URLS:
        if not is_pay_user and len(rets) > 0:
            break
        rets.extend(search(query, URL))
    return rets

def search(query, url):
    rets =[]
    try:
        curdir = os.path.dirname(os.path.abspath(__file__))
        shell_cmd =  "sh {}/curl_uukk.sh {} {} \"{}\"".format(curdir, query, url, COOKIE)
        #print(shell_cmd)
        return_cmd = subprocess.run(shell_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8',shell=True)
        if return_cmd.returncode == 0:
            ret_val = return_cmd.stdout
            js = json.loads(ret_val)
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
    except:
        print(traceback.format_exc())
    return rets

print(get_from_uukk("繁花", True))
