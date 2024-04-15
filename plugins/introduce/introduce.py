#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
import json
import re
import plugins
from bridge.context import ContextType
from channel.chat_message import ChatMessage
from bridge.reply import Reply, ReplyType
from plugins import *
import time
import traceback
from common.log import logger
from .util import *
import datetime

@plugins.register(
    name="introduce",                         # 插件的名称
    desire_priority=500,                    # 插件的优先级
    hidden=False,                         # 插件是否隐藏
    desc="群机器人功能介绍",        # 插件的描述
    version="0.0.1",                      # 插件的版本号
    author="gloarysaladin",                       # 插件的作者
)


class Introduce(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        try:
            self.conf = super().load_config()
            self.curdir = os.path.dirname(__file__)
            logger.info("[introduce] inited")
        except:
            logger.error("failed to init introduce. {}".format(traceback.format_exc()))
            raise self.handle_error(e, "[introduce] init failed, ignore ")

    def on_handle_context(self, e_context: EventContext):
        self.conf = super().load_config()
        context = e_context['context']
        content = e_context["context"].content
        if context.type == ContextType.MSG_BUSY:
            self.send_busy_notice(e_context)
            return
            
        if content == "功能介绍":
            conf = super().load_config()
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本

            useage_path = os.path.join(self.curdir, "useage.txt")
            msg = self.load_file(useage_path)
            reply.content = f"{msg}"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS 

        if content == "开启新朋友消息":
            self.conf["accept_friend_msg"] = True
            super().save_config(self.conf)
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            reply.content = "已开启添加新朋友欢迎消息"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS 


        if content == "关闭新朋友消息":
            self.conf["accept_friend_msg"] = False
            super().save_config(self.conf)
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            reply.content = "已关闭添加新朋友欢迎消息"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS 

        if content.strip().startswith("添加小红书cookie"):
            self.add_xhs_cookie(e_context)
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            reply.content = "已添加" 
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

        if  content.startswith("我是") or content.startswith("I'm") or (self.conf["accept_friend_msg"] and e_context["context"].type == ContextType.ACCEPT_FRIEND):
            if self.conf["open_movie_search"]:
                self.send_favorite_movie(e_context)

            e_context["context"].type = ContextType.TEXT
            msg: ChatMessage = e_context["context"]["msg"]
            logger.info(f"start to welcome {msg.from_user_nickname}.")
            e_context["context"].content = f'以你好作为欢迎语开头， 提示一定要以 找资源名 格式找资源, 并用 找还珠格格 举例。建议他收藏我方便以后查找资源。最后发一句日常的祝福语。'
            #e_context["context"].content = f'写一句话抱歉的话告诉对方, 小助手已经没法给大家提供资源搜索了, 因为被别人多次投诉。如果你想继续找资源的话，可以加入链接里的微信群：https://sourl.cn/m2ut6M , 群满之后就不再加人了; 抱歉的话一定要带上上面的微信群链接。'
            e_context.action = EventAction.BREAK  # 事件结束，进入默认处理逻辑
            return
           
        if content == "娱乐一下":
            # 发送图片
            self.ent_datas = {}
            ent_data_path=os.path.join(self.curdir, "ent_datas.pkl")
            if os.path.exists(ent_data_path):
                self.ent_datas = read_pickle(ent_data_path)
            imageUrls=""
            comments=[]
            for key in self.ent_datas:
                if self.ent_datas[key]["is_used"]:
                    continue
                imageUrls = self.ent_datas[key]["url"]
                comments = self.ent_datas[key]["comments"]
                break

            receivers = e_context["context"].kwargs["receiver"]
            image_url_list = imageUrls.split(",")
            for imageUrl in image_url_list:
                rc = img_to_jpeg(imageUrl)
                logger.info("imgurl={}".format(imageUrl))
                send(rc, e_context, ReplyType.IMAGE)
            if len(image_url_list) > 0:
                time.sleep(self.conf['interval'])

            for comment in comments[:-1]:
                e_context['context'].kwargs['receiver'] = receivers
                e_context['context'].kwargs['session_id'] = receivers
                send(comment, e_context, ReplyType.TEXT)
                time.sleep(3)

            e_context['context'].kwargs['receiver'] = receivers
            e_context['context'].kwargs['session_id'] = receivers
            send2(comments[-1], e_context, ReplyType.TEXT)
            self.ent_datas[key]["is_used"] = True
            write_pickle(ent_data_path, self.ent_datas)
    
    def send_favorite_movie(self, e_context: EventContext):
        context = e_context['context']
        isgroup = context.get("isgroup", False)
        self.favorite_movie_path = self.conf["favorite_movie"] 
        favorite_movie_datas = {}
        if os.path.exists(self.favorite_movie_path):
            favorite_movie_datas = read_pickle(self.favorite_movie_path)
        rets = []
        for key in favorite_movie_datas:
            rets.append("{}".format(favorite_movie_datas[key]))
        if len (rets) > 0:
            rets.append("----------------------------")
            rets.append("提示：\n1. 夸克会显示试看2分钟，转存到自己的夸克网盘就能看完整的视频.")
            rets.append("2. 不能保证都可以观看，自己试.")
            rets.append("3. 资源均源于互联网，仅供交流学习，看完请删除.")
            if not isgroup:
                rets.append("4. ‼️进资源群，海量资源免费： https://sourl.cn/m2ut6M ")
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            rets.append(formatted_time)
            rets.insert(0, "-------热门资源推荐--------")
        if len(rets) > 0:
            msg: ChatMessage = context["msg"]
            uid = msg.from_user_id if not isgroup else msg.actual_user_id
            try:
                itchat.send("\n".join(rets), uid)
            except:
                print("uid={}".format(uid), traceback.format_exc())
    
    def send_busy_notice(self, e_context: EventContext):
        context = e_context['context']
        msg: ChatMessage = context["msg"]
        isgroup = context.get("isgroup", False)
        uid = msg.from_user_id if not isgroup else msg.actual_user_id
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        notice = "消息发送过于频繁 {}".format(formatted_time)
        try:
            reciver = self.conf["busy_msg_reciver"] 
            friend = itchat.search_friends(name=reciver)
            itchat.send(notice, friend[0]["UserName"])
        except:
            pass

    def load_file(self, input_path):
        f = open(input_path)
        lines = []
        for line in f.readlines():
            if line.strip().startswith("#"):
                continue
            lines.append(line.strip())
        return "\n".join(lines)

    def add_xhs_cookie(self, e_context):
        content = e_context['context'].content
        cookie = content.replace("添加小红书cookie", "").strip()
        conf = super().load_config()
        cookie_path=conf["xhs_cookie_file"]
        with open(cookie_path, 'a') as f:
            f.write(cookie+"\n")

    def get_help_text(self, **kwargs):
        help_text = "发送关键词执行对应操作\n"
        help_text += "输入 '功能介绍'， 将获得机器人的功能介绍.\n"
        help_text += "输入 '添加小红书cookie+cookiestr'， 添加小红书cookie.\n"
        help_text += "输入 '开启新朋友消息'， 接受新朋友时将发送欢迎消息.\n"
        help_text += "输入 '关闭新朋友消息'， 接受新朋友时将不发送欢迎消息.\n"
        return help_text
