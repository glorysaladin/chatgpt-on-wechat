import os

import pickle

os.getcwd()

#os.chdir("文件所在的路径")

file = open("ent_datas.pkl","rb")
#file = open("user_info.pkl","rb")

content = pickle.load(file)

print(content)
