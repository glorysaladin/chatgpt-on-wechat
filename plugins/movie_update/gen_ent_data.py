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
ent_datas_path = os.path.join(curdir, "moviename_whitelist.pkl")

ent_datas = {}
if os.path.exists(ent_datas_path):
   ent_datas = read_pickle(ent_datas_path)

f_ori = open(sys.argv[1])
for line in f_ori.readlines():
    items = line.strip().split("\t")
    moviename = items[0]
    ent_datas[moviename] = items[1]

# 娱乐数据更新
write_pickle(ent_datas_path, ent_datas)
