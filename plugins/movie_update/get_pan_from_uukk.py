# -*- coding: utf-8 -*-
import subprocess, json, os

def good_match(s1, s2):
    set1 = set(s1)
    set2 = set(s2)
    common_chars = set1.intersection(set2)
    if len(common_chars)*1.0  / (len(set1) + 0.1) > 0.6:
       return True 
    return False

def get_from_uukk(query):
    curdir = os.path.dirname(__file__)
    shell_cmd =  "sh {}/curl_uukk.sh {}".format(curdir, query)
    #shell_cmd =  "sh ./curl_uukk.sh {}".format(query)
    print(shell_cmd)
    return_cmd = subprocess.run(shell_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8',shell=True)
    rets =[]
    if return_cmd.returncode == 0:
        ret_val = return_cmd.stdout
        js = json.loads(ret_val)
        for item in js["list"]:
            question=item['question']
            answer=item["answer"]
            if "失效" in question:
                continue
            answer = answer.replace("链接：", "\n")
            if good_match(query, question):
                rets.append(answer)
    return rets
print(get_from_uukk("以爱为营"))
