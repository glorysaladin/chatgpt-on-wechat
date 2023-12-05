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

@plugins.register(
    name="introduce",                         # 插件的名称
    desire_priority=50,                    # 插件的优先级
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
        if e_context["context"].type != ContextType.TEXT:
            return
        self.conf = super().load_config()
        content = e_context["context"].content
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

        if content.startswith("我是") or content.startswith("I'm") or (self.conf["accept_friend_msg"] and e_context["context"].type == ContextType.ACCEPT_FRIEND):
            e_context["context"].type = ContextType.TEXT
            msg: ChatMessage = e_context["context"]["msg"]
            logger.info(f"start to welcome {msg.from_user_nickname}.")
            e_context["context"].content = f'以你好作为欢迎语开头， 提示一定要以"找资源名"格式找资源, 并用"找还珠格格"举例, 建议他收藏我方便以后查找资源。最后添加一句随机的祝福语。上面的欢迎语要控制在50个字以内。'
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
            e_context.action = EventAction.BREAK_PASS 
       
    def load_file(self, input_path):
        f = open(input_path)
        lines = []
        for line in f.readlines():
            if line.strip().startswith("#"):
                continue
            lines.append(line.strip())
        return "\n".join(lines)

    def get_help_text(self, **kwargs):
        help_text = "发送关键词执行对应操作\n"
        help_text += "输入 '功能介绍'， 将获得机器人的功能介绍.\n"
        help_text += "输入 '开启新朋友消息'， 接受新朋友时将发送欢迎消息.\n"
        help_text += "输入 '关闭新朋友消息'， 接受新朋友时将不发送欢迎消息.\n"
        return help_text
