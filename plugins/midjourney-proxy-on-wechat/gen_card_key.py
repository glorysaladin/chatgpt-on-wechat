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
card_datas_path = os.path.join(curdir, "card_datas.pkl")
card_data_txt_path = os.path.join(curdir, "card_datas.txt")

card_datas = {}
if os.path.exists(card_datas_path):
   card_datas = read_pickle(card_datas_path)
output=open(card_data_txt_path, "w+")
for i in range(0, 800):
    key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))
    random_number = random.randint(0, 7)
    limit= [1, 2, 5,  10, 20, 50, 100, 100000]
    price = [3, 5, 10, 18, 36, 80, 140, 199]
    #print("{}\t{}\t{}".format(random_str, li[random_number], p[random_number]))
    if key in card_datas:
        continue
    info={'limit':0, 'is_used':False, 'used_date':'', 'used_user_id':'', 'used_user_name':''}
    info['limit']=limit[random_number]
    card_datas[key] = info
    output.write("{}\t{}\t{}\n".format(key, limit[random_number], price[random_number]))
output.close()

# 卡密数据更新
write_pickle(card_datas_path, card_datas)
