import os

import pickle

os.getcwd()

#os.chdir("文件所在的路径")

#file = open("moviename_whitelist.pkl","rb")
file = open("user_datas.pkl","rb")

content = pickle.load(file)

print(content)
