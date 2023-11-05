#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
import json
import re
import plugins
from bridge.reply import Reply, ReplyType
from plugins import *
from .movie_util import *


@plugins.register(
    name="movie_update",                         # 插件的名称
    desire_priority=1,                    # 插件的优先级
    hidden=False,                         # 插件是否隐藏
    desc="获取影视资源更新数据",        # 插件的描述
    version="0.0.1",                      # 插件的版本号
    author="gloarysaladin",                       # 插件的作者
)


class MovieUpdate(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        try:
            self.conf = super().load_config()
            print("[movie_update] inited")
        except:
            raise self.handle_error(e, "[movie_update] init failed, ignore ")

    def on_handle_context(self, e_context: EventContext):
        content = e_context["context"].content
        if content == "电影更新":
            conf = super().load_config()
            post_id = conf["post_id"]
            print("movie_update: post_id = {}".format(post_id))
            (last_post_id, msg) = get_movie_update(post_id)
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            reply.content = f"{msg}"
            e_context["reply"] = reply
            conf["post_id"] = last_post_id
            super().save_config(conf)
            e_context.action = EventAction.BREAK_PASS
        if content.startswith("找"):
            conf = super().load_config()
            weburl= conf["web_url"]
            moviename=content.strip().replace("找","")
            moviename=moviename.replace("电影", "").replace("电视剧", "").replace("韩剧", "").replace("完整版", "").replace("未删减版", "").replace("未删减","").replace("无删减", "").replace("+","")
            msg = search_movie(weburl, moviename)
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            reply.content = f"{msg}"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            
    def get_help_text(self, **kwargs):
        help_text = "发送关键词执行对应操作\n"
        help_text += "输入 '电影更新'， 将获取今日更新的电影\n"
        help_text += "输入 '找三体'， 将获取三体资源\n"
        return help_text
