#!/usr/bin/env python
# -*- coding:utf-8 -*-
import requests
import json
import re
import plugins
from bridge.reply import Reply, ReplyType
from plugins import *
from .movie_util import *
import traceback
from common.log import logger
from .util import *

@plugins.register(
    name="movie_update",                         # 插件的名称
    desire_priority=1,                    # 插件的优先级
    hidden=False,                         # 插件是否隐藏
    desc="获取影视资源更新数据",        # 插件的描述
    version="0.0.2",                      # 插件的版本号
    author="gloarysaladin",                       # 插件的作者
)
class MovieUpdate(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        try:
            self.conf = super().load_config()
            self.curdir = os.path.dirname(__file__)
            ads_path = os.path.join(self.curdir, "ads.txt")
            self.ads_content = self.load_ads(ads_path)
            logger.info("[movie_update] ads_content={}".format(self.ads_content))
            logger.info("[movie_update] inited")
        except:
            logger.error("[movie_update] inited failed.", traceback.format_exc())
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

            reply.content += "\n\n"
            reply.content += "------官方优惠🧧------\n"
            reply.content += self.ads_content
            e_context["reply"] = reply
            conf["post_id"] = last_post_id
            super().save_config(conf)
            e_context.action = EventAction.BREAK_PASS

        if content.strip().startswith("加入资源白名单"):
            content = content.replace("加入资源白名单","")
            self.add_movie_to_whitelist(content.strip())
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            reply.content = f"{content} 成功加入白名单."
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return

        if content.startswith("找") or self.is_whitelist_movie(content):
            conf = super().load_config()
            weburl= conf["web_url"]
            moviename=content.strip().replace("找","")
            invalid_terms=["电影", "电视剧", "韩剧", "动漫", "完整版", "未删减版", "未删减", "无删减", "+", "资源" "\"", "”", "“", "《", "》"]
            for term in invalid_terms:
                moviename = moviename.replace(term , "")
            ret, msg = search_movie(weburl, moviename)
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            reply.content = f"{msg}"
            if ret:
                reply.content += "\n"
                reply.content += "---------------------------\n"
                reply.content += "🥳 方便好用，分享给朋友 [庆祝]\n"
                reply.content += "[爱心]邀请我进其他群，服务更多伙伴🌹\n"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

    def load_ads(self, ads_path):
        f = open(ads_path)
        lines = []
        for line in f.readlines():
            if line.strip().startswith("#"):
                continue
            lines.append(line.strip())
        return "\n".join(lines)

    def is_whitelist_movie(self, moviename):
        if len(moviename) > 20:
            return False
        self.movie_whitelist_datas = {}
        movie_whitelist_data_path=os.path.join(self.curdir, "moviename_whitelist.pkl")
        if os.path.exists(movie_whitelist_data_path):
            self.movie_whitelist_datas = read_pickle(movie_whitelist_data_path)
        for white_movie in self.movie_whitelist_datas:
            if white_movie in moviename:
                return True
        return False

    def add_movie_to_whitelist(self, moviename):
        self.movie_whitelist_datas = {}
        movie_whitelist_data_path=os.path.join(self.curdir, "moviename_whitelist.pkl")
        if os.path.exists(movie_whitelist_data_path):
            self.movie_whitelist_datas = read_pickle(movie_whitelist_data_path)

        if moviename not in self.movie_whitelist_datas:
            self.movie_whitelist_datas[moviename] = True
            write_pickle(movie_whitelist_data_path, self.movie_whitelist_datas)

    def get_help_text(self, **kwargs):
        help_text = "发送关键词执行对应操作\n"
        help_text += "输入 '电影更新'， 将获取今日更新的电影\n"
        help_text += "输入 '找三体'， 将获取三体资源\n"
        help_text += "输入 '加入资源白名单+资源名'， 将资源加入到白名单中\n"
        return help_text
