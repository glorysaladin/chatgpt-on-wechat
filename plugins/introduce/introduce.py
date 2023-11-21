#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
import json
import re
import plugins
from bridge.reply import Reply, ReplyType
from plugins import *
import time
import traceback
from common.log import logger
from .util import *

@plugins.register(
    name="introduce",                         # 插件的名称
    desire_priority=1,                    # 插件的优先级
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
        if content == "娱乐一下":
            # 发送图片
            self.ent_datas = {}
            ent_data_path=os.path.join(self.curdir, "ent_datas.pkl")
            if os.path.exists(ent_data_path):
                self.ent_datas = read_pickle(ent_data_path)
            imageUrl=""
            comments=[]
            for key in self.ent_datas:
                if self.ent_datas[key]["is_used"]:
                    continue
                imageUrl = self.ent_datas[key]["url"]
                comments = self.ent_datas[key]["comments"]
                break

            receivers = e_context["context"].kwargs["receiver"]
            if len(imageUrl) > 0:
                rc = img_to_jpeg(imageUrl)
                logger.info("imgurl={}".format(imageUrl))
                send(rc, e_context, ReplyType.IMAGE)
                time.sleep(self.conf['interval'])

            for comment in comments:
                e_context['context'].kwargs['receiver'] = receivers
                e_context['context'].kwargs['session_id'] = receivers
                send2(comment, e_context, ReplyType.TEXT)
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
        help_text += "输入 '功能介绍'， 将获得机器人的功能介绍."
        return help_text
