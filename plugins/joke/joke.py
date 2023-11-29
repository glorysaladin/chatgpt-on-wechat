#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
import json
import re
import plugins
from bridge.reply import Reply, ReplyType
from plugins import *

@plugins.register(
    name="joke",                         # 插件的名称
    desire_priority=1,                    # 插件的优先级
    hidden=False,                         # 插件是否隐藏
    desc="发送笑话",        # 插件的描述
    version="0.0.1",                      # 插件的版本号
    author="gloarysaladin",                       # 插件的作者
)
class Joke(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[Joke] inited")

    def on_handle_context(self, e_context: EventContext):
        content = e_context["context"].content
        if content.startswith("笑话"):
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            msg = self.get_joke()
            reply.content = f"{msg}"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

    def get_joke(self):
        url = "https://v2.alapi.cn/api/joke/random"
        payload = "token=rQYivEZrM6FWmxcZ"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        response = requests.request("POST", url, data=payload, headers=headers)
        js = json.loads(response.text)
        try:
            data = js["data"]
            title = data["title"]
            content = data["content"]
            return "【开心一笑】{}\n\n{}".format(title, content)
        except:
            pass
        return ""

    def get_help_text(self, **kwargs):
        help_text = ""
        return help_text
