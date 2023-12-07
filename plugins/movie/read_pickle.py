import os

import pickle

def read_pickle(path):
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data

def write_pickle(path, content):
    with open(path, "wb") as f:
        pickle.dump(content, f)
    return True

#os.chdir("文件所在的路径")

#file = open("user_datas.pkl","rb")

#content = pickle.load(file)

user_datas = read_pickle("user_datas.pkl")
for key in user_datas:
    if not user_datas[key]["is_pay_user"]:
        if user_datas[key]['limit'] > 1:
            user_datas[key]['limit'] = 0
       
    #print(key, user_datas[key])
#
write_pickle("user_datas.pkl", user_datas)
