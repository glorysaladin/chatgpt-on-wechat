import random
import string
import sys, os

import pickle

def write_pickle(path, content):
    with open(path, "wb") as f:
        pickle.dump(content, f)
    return True

def read_pickle(path):
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data

# 读取和写入配置文件
curdir = os.path.dirname(__file__)
ent_datas_path = os.path.join(curdir, "ent_datas.pkl")

ent_datas = {}
if os.path.exists(ent_datas_path):
   ent_datas = read_pickle(ent_datas_path)

f_ori = open(sys.argv[1])
for line in f_ori.readlines():
    items = line.strip().split("\t")
    id = items[0]

    #if id in ent_datas:
    #    continue

    url = items[1]
    data_info = {
        "url": "",
        "comments": [],
        "is_used": False
    }
    data_info["url"] = url
    data_info["is_used"] = False
    for i in range(2, len(items)):
        data_info["comments"].append(items[i])

    ent_datas[id] = data_info

# 娱乐数据更新
write_pickle(ent_datas_path, ent_datas)
