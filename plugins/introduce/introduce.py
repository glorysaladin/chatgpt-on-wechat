#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
import json
import re
import plugins
from bridge.reply import Reply, ReplyType
from plugins import *


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
            print("[introduce] inited")
        except:
            raise self.handle_error(e, "[introduce] init failed, ignore ")

    def on_handle_context(self, e_context: EventContext):
        content = e_context["context"].content
        if content == "功能介绍":
            conf = super().load_config()
            msg = self.conf["introduce"]
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            reply.content = f"{msg}"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

    def get_help_text(self, **kwargs):
        help_text = "发送关键词执行对应操作\n"
        help_text += "输入 '功能介绍'， 将获得机器人的功能介绍."
        return help_text
