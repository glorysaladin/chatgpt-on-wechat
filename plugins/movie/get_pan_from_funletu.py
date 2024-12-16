# -*- coding: utf-8 -*-
import subprocess, json, os

def good_match(s1, s2):
    set1 = set(s1)
    set2 = set(s2)
    common_chars = set1.intersection(set2)
    if len(common_chars)*1.0  / (len(set1) + 0.1) > 0.4:
       return True 
    return False

def get_from_funletu(query):
    curdir=os.path.dirname(os.path.abspath(__file__))
    shell_cmd =  "sh {}/curl_funletu.sh {}".format(curdir, query)
   # print(shell_cmd)
    return_cmd = subprocess.run(shell_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8',shell=True)
    rets =[]
    if return_cmd.returncode == 0:
        ret_val = return_cmd.stdout
        js = json.loads(ret_val)
        for item in js["data"]:
            title=item["title"]
            if "失效" in title:
                continue
            url = item["url"].replace("?entry=funletu", "")
            if good_match(query, title):
                rets.append("{}\n{}".format(title, url))
    return rets
print(get_from_funletu("庆余年"))
