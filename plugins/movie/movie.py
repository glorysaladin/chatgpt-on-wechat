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
from bridge.context import ContextType
import datetime
from lib import itchat
from lib.itchat.content import *
import random

@plugins.register(
    name="movie",                         # 插件的名称
    desire_priority=100,                    # 插件的优先级
    hidden=False,                         # 插件是否隐藏
    desc="获取影视资源更新数据",        # 插件的描述
    version="0.0.3",                      # 插件的版本号
    author="gloarysaladin",                       # 插件的作者
)
class Movie(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        try:
            self.conf = super().load_config()
            self.curdir = os.path.dirname(__file__)
            ads_path = os.path.join(self.curdir, "ads.txt")
            if not os.path.isfile(ads_path):
                with open(ads_path, 'w') as f:
                   pass

            self.ads_content = self.load_ads(ads_path)

            self.user_datas = {}
            self.user_datas_path = os.path.join(self.curdir, "user_datas.pkl")
            if os.path.exists(self.user_datas_path):
                self.user_datas = read_pickle(self.user_datas_path)

            self.card_datas = {}
            self.card_datas_path = self.conf["movie_cards"]
            if os.path.exists(self.card_datas_path):
                self.card_datas = read_pickle(self.card_datas_path)

            self.ads_datas = {}
            self.ads_datas_path = self.conf["ads"]
            if os.path.exists(self.ads_datas_path):
                self.ads_datas = read_pickle(self.ads_datas_path)

            logger.info("[movie] daily_limit={} ads_content={}".format(self.conf['daily_limit'], self.ads_content))
            logger.info("[movie] inited")
        except:
            logger.error("[movie] inited failed.", traceback.format_exc())
            raise self.handle_error(e, "[movie] init failed, ignore ")

    def on_handle_context(self, e_context: EventContext):
        logger.debug("movie={}".format(e_context))
        context = e_context['context']
        content = context.content
        if context.type == ContextType.MSG_BUSY:
            return
        if content == "电影更新":
            conf = super().load_config()
            post_id = conf["post_id"]
            print("movie: post_id = {}".format(post_id))
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

        if content.strip().startswith("添加广告"):
            self.add_ads(e_context)
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            reply.content = f"添加广告成功."
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return

        if content.strip().startswith("关闭广告"):
            conf = super().load_config()
            conf["open_ads"] = False
            super().save_config(conf)
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            reply.content = f"关闭广告成功."
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return

        if content.strip().startswith("开启广告"):
            conf = super().load_config()
            conf["open_ads"] = True
            super().save_config(conf)
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            reply.content = "开启广告成功."
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return

        if content.strip().startswith("删除广告"):
            self.del_ads(e_context)
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            reply.content = "删除广告成功."
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return

        if content.strip().startswith("固定广告"):
            self.set_fixed_ad_id(e_context)
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            reply.content = "设置固定广告成功."
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return

        if content.strip().startswith("所有广告"):
            all_ads = self.get_all_ads()
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            reply.content = "{}".format(all_ads)
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return

        if context.type == ContextType.MONEY:
            self.recharge_with_money(e_context)
            self.send_money_msg(e_context)
            e_context["context"].type = ContextType.TEXT
            msg: ChatMessage = e_context["context"]["msg"]
            e_context["context"].content = f"请感谢对方的红包奖励，告诉他将继续努力为对方寻找需要的影视资源。"
            e_context.action = EventAction.BREAK  # 事件结束，进入默认处理逻辑
            return

        if content.strip() == "你好" or content.strip() == "您好" or content.strip() == "谢谢" or content.strip() == "多谢":
            return

        #if ContextType.TEXT == context.type and "资源充值" in content:
        # 所有的消息都检查是否是充值
        if ContextType.TEXT == context.type:
            if self.recharge(e_context):
                return

        if ContextType.TEXT == context.type and "资源余额" in content:
            self.userInfo = self.get_user_info(e_context)
            return self.check_limit(e_context)
                
        only_affdz = True
        if content.startswith("找") or self.is_whitelist_movie(content):
            only_affdz = False
         
        self.userInfo = self.get_user_info(e_context)
        logger.info('Cur User Info = {}, only_affdz={}'.format(self.userInfo, only_affdz))

        moviename=content.strip().replace("找","")
        invalid_terms=["电影", "电视剧", "韩剧", "动漫", "完整版", "未删减版", "未删减", "无删减", "，","," "+", "资源" "\"", "”", "“", "《", "》", "谢谢", "\'" , "【","】", "[", "]", "➕"]
        for term in invalid_terms:
            moviename = moviename.replace(term , "")
        is_new_movie = self.is_new_search_word(self.userInfo['search_words'], moviename)
      
        if is_new_movie and not self.userInfo['isgroup'] and self.userInfo["limit"] <= 0 and self.userInfo['user_nickname'] != '阿木达':
            current_time = datetime.datetime.now()
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            #reply = Reply(ReplyType.ERROR, "额度已用完，服务链接了20个全网最全最新的影视资源库，这里搜不到的其他地方也没有。 继续使用请充值：\nhttps://sourl.cn/8VBSBe \n{}".format(formatted_time)) 
            reply = Reply()
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            reply.content = "非常感谢您的支持，请您发个 1元以上的红包作为鼓励, 就可以继续资源搜索功能，同时可以享受夸克、百度、迅雷等多个网盘的资源搜索服务."
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            #e_context["context"].type = ContextType.TEXT
            #msg: ChatMessage = e_context["context"]["msg"]
            #e_context["context"].content = f"请让对方给你发送一个红包作为鼓励，发送之后可以继续使用资源搜索服务。"
            #e_context.action = EventAction.BREAK  # 事件结束，进入默认处理逻辑
            return

        weburl= self.conf["web_url"]
        ret, msg = search_movie(weburl, moviename, self.userInfo['ispayuser'], only_affdz)
        if only_affdz and not ret:
            return
        else:
            reply = Reply()  # 创建回复消息对象
            reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
            reply.content = f"{msg}"
            if ret:
                if is_new_movie:
                    self.user_datas[self.userInfo['user_key']]["limit"] -= 1
                    self.user_datas[self.userInfo['user_key']]["search_words"].append(moviename)
                    write_pickle(self.user_datas_path, self.user_datas)

                reply.content += "\n\n"
                reply.content += "------------------------------\n"
                #if self.user_datas[self.userInfo['user_key']]['is_pay_user']:
                #    reply.content += "您剩余 {} 次资源搜索\n".format(self.user_datas[self.userInfo['user_key']]["limit"])
                reply.content += "提示：夸克会显示试看2分钟，转存到自己的夸克网盘就能看完整的视频.\n"
                #reply.content += "🥳 方便好用，分享给朋友 [庆祝]\n"
                #reply.content += "[爱心]邀请我进其他群，服务更多伙伴🌹\n"
                #if not self.userInfo['isgroup']:
                #    reply.content += "资源免费分享的，能帮到你请随意打赏点辛苦费吧🌹\n"
                current_time = datetime.datetime.now()
                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
                reply.content += formatted_time + "\n"

            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            movie_ads_content = self.get_rand_ads() 

            msg: ChatMessage = context["msg"]
            isgroup = context.get("isgroup", False)
            # 写入用户信息，企业微信没有from_user_nickname，所以使用from_user_id代替
            uid = msg.from_user_id if not isgroup else msg.actual_user_id
            conf = super().load_config()
            if len(movie_ads_content) > 2 and conf["open_ads"]:
                itchat.send(movie_ads_content, uid)

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
        movie_whitelist_data_path=self.conf['movie_whitelist']
        if os.path.exists(movie_whitelist_data_path):
            self.movie_whitelist_datas = read_pickle(movie_whitelist_data_path)
        for white_movie in self.movie_whitelist_datas:
            if white_movie in moviename:
                return True
        return False

    def add_movie_to_whitelist(self, moviename):
        self.movie_whitelist_datas = {}
        movie_whitelist_data_path=self.conf['movie_whitelist']
        if os.path.exists(movie_whitelist_data_path):
            self.movie_whitelist_datas = read_pickle(movie_whitelist_data_path)

        if moviename not in self.movie_whitelist_datas:
            self.movie_whitelist_datas[moviename] = True
            write_pickle(movie_whitelist_data_path, self.movie_whitelist_datas)

    def get_user_info(self, e_context: EventContext):
        # 获取当前时间戳
        current_timestamp = time.time()
        # 将当前时间戳和给定时间戳转换为日期字符串
        current_date = time.strftime("%Y-%m-%d", time.localtime(current_timestamp))
        context = e_context['context']
        msg: ChatMessage = context["msg"]
        isgroup = context.get("isgroup", False)

        # 写入用户信息，企业微信没有from_user_nickname，所以使用from_user_id代替
        uid = msg.from_user_id if not isgroup else msg.actual_user_id
        uname = (msg.from_user_nickname if msg.from_user_nickname else uid) if not isgroup else msg.actual_user_nickname

        user_key = ""
        if isgroup:
            logger.info('Group Info = {}'.format(msg))
            NickName = uname
            user_key = "{}|{}|{}|{}".format("", "", "", NickName)
        else:
            friendInfo = itchat.get_friend_info(uid)
            logger.info('Frinend Info = {}'.format(friendInfo))
            try:
                Province = friendInfo.get("Province", "")
                City = friendInfo.get("City", "")
                Sex = friendInfo.get("Sex", "")
                NickName = friendInfo.get("NickName", "")
                user_key = "{}|{}|{}|{}".format(Province, City, Sex, NickName)
            except:
               logger.error(traceback.format_exc())
        logger.info("user_key={}".format(user_key))

        userInfo = {
            "user_id": uid,
            "user_nickname": uname,
            "user_key": user_key,
            "isgroup": isgroup,
            "group_id": msg.from_user_id if isgroup else "",
            "group_name": msg.from_user_nickname if isgroup else "",
        }

        if user_key not in self.user_datas:
            # 纯新用户，数据写入
            u_data = {
                "limit": self.conf["daily_limit"],
                "time": current_date,
                "is_pay_user": False,
                "search_words" : []
            }
            self.user_datas[user_key] = u_data
            write_pickle(self.user_datas_path, self.user_datas)
        """
        else:
            # 老用户， 数据更新写入
            # 判断是否是新的一天
            if self.user_datas[user_key]["time"] != current_date:
                if not self.user_datas[user_key]["is_pay_user"]:
                    u_data = {
                        "limit": self.conf["daily_limit"],
                        "time": current_date,
                        "is_pay_user": False,
                    }
                    self.user_datas[user_key] = u_data
                else:
                    self.user_datas[user_key]['time'] = current_date
                write_pickle(self.user_datas_path, self.user_datas)
        """
        limit = self.user_datas[user_key]["limit"] if "limit" in self.user_datas[user_key] and self.user_datas[user_key]["limit"] else False
        userInfo['limit'] = limit
        userInfo['ispayuser'] = self.user_datas[user_key]["is_pay_user"]
        userInfo['search_words'] = self.user_datas[user_key]['search_words']
        return userInfo

    def send_money_msg(self, e_context: EventContext):
        context = e_context['context']
        msg: ChatMessage = context["msg"]
        isgroup = context.get("isgroup", False)
        uid = msg.from_user_id if not isgroup else msg.actual_user_id
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        user_key = "None 发了一个红包 \n{}".format(formatted_time)
        try:
            friendInfo = itchat.get_friend_info(uid)
            Province = friendInfo.get("Province", "")
            City = friendInfo.get("City", "")
            Sex = friendInfo.get("Sex", "")
            Signature = friendInfo.get("Signature", "")
            NickName = friendInfo.get("NickName", "")
            user_key = "{} 发了一个红包\n省：{}\n市：{}\n性别：{}\n签名：{}\n时间：{}".format(NickName, Province, City, Sex, Signature,  formatted_time)

            friend = itchat.search_friends(name='张五航')
            #logger.info("friend info ={}".format(friend))
            me = friend[0]["UserName"]
            itchat.send(user_key, me)
        except:
            pass


    def recharge_with_money(self, e_context: EventContext):
        # 获取用户信息，进行充值
        self.userInfo = self.get_user_info(e_context)
        user_id = self.userInfo['user_id']
        user_key = self.userInfo['user_key']
        user_name = self.userInfo['user_nickname']
        if self.user_datas[user_key]['limit'] < 0:
            self.user_datas[user_key]['limit'] = 0
        self.user_datas[user_key]['limit'] += 10
        # 设置为付费用户
        self.user_datas[user_key]['is_pay_user'] = True
        # 数据更新
        write_pickle(self.user_datas_path, self.user_datas)
    
    # 用户充值
    def recharge(self, e_context: EventContext):
        content = e_context['context'].content
        pattern=r"([a-zA-Z0-9]+)"
        keys = re.findall(pattern, content)
        key = ""
        if len(keys) > 0:
            key = keys[0]
        # 卡密的长度设置为固定的20
        if len(key) != 20:
            return False

        # 获取用户信息，进行充值
        self.userInfo = self.get_user_info(e_context)
        user_id = self.userInfo['user_id']
        user_key = self.userInfo['user_key']
        user_name = self.userInfo['user_nickname']
        # 检验卡密是否有效
        card_exist = False
        card_used = False
        if key in self.card_datas:
            card_exist = True
            if self.card_datas[key]['is_used'] == False:
                # 次数充值
                if self.user_datas[user_key]['limit'] < 0 :
                    self.user_datas[user_key]['limit'] = 0
                self.user_datas[user_key]['limit'] += self.card_datas[key]['limit']
                # 设置为付费用户
                self.user_datas[user_key]['is_pay_user'] = True
                # 数据更新
                write_pickle(self.user_datas_path, self.user_datas)
                
                # 设置卡的状态
                self.card_datas[key]['is_used'] = True
                current_time = datetime.datetime.now()
                formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
                self.card_datas[key]['used_date'] = formatted_time
                self.card_datas[key]['used_user_id'] = user_id
                self.card_datas[key]['used_user_name'] = user_name
                # 卡密数据更新
                write_pickle(self.card_datas_path, self.card_datas)
            else:
                card_used=True
        else:
            card_exist=False

        reply = Reply()  # 创建回复消息对象
        reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本

        if not card_exist:
            key="|".join(keys)
            reply.content = "卡密[{}]不存在,请联系客服确认.".format(key)
        if card_used:
            key="|".join(keys)
            reply.content = "卡密[{}]已被用户【{}】在【{}】充值使用,请确认.".format(key, self.card_datas[key]['used_user_name'], self.card_datas[key]['used_date'])
        if card_exist and not card_used:
            reply.content = "恭喜您充值成功, 当前剩余额度[ {} ]次.".format(self.user_datas[user_key]['limit'])
        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS
        return True

    def add_ads(self, e_context: EventContext):
        self.ads_datas = {}
        self.ads_datas_path = self.conf["ads"]
        if os.path.exists(self.ads_datas_path):
            self.ads_datas = read_pickle(self.ads_datas_path)
        rand_num = str(random.randint(0,10000))
        content = e_context['context'].content
        content = content.replace("添加广告", "")
        self.ads_datas[rand_num] = content 
        write_pickle(self.ads_datas_path, self.ads_datas)

    def del_ads(self, e_context: EventContext):
        self.ads_datas = {}
        self.ads_datas_path = self.conf["ads"]
        if os.path.exists(self.ads_datas_path):
            self.ads_datas = read_pickle(self.ads_datas_path)
        content = e_context['context'].content
        content = content.replace("删除广告", "")
        try:
            del self.ads_datas[content.strip()]
            write_pickle(self.ads_datas_path, self.ads_datas)
        except:
            pass

    def set_fixed_ad_id(self, e_context: EventContext):
        self.conf = super().load_config()
        content = e_context['context'].content
        content = content.replace("固定广告", "")
        self.conf["fixed_ads_id"] = content.strip()
        super().save_config(conf)

    def get_rand_ads(self):
        try:
            self.ads_datas = {}
            self.ads_datas_path = self.conf["ads"]
            if os.path.exists(self.ads_datas_path):
                self.ads_datas = read_pickle(self.ads_datas_path)
            if len(self.ads_datas) > 0:
                self.conf = super().load_config()
                rand_key = ""
                if self.conf["fixed_ads_id"] != "":
                    rand_key = self.conf["fixed_ads_id"]
                else:
                    rand_num = random.randint(0, len(self.ads_datas) - 1)
                    keys = list(self.ads_datas.keys())
                    rand_key = keys[rand_num]
                    logger.info("rand_num={} rand_key={}".format(rand_num, rand_key))
                return self.ads_datas[rand_key]
            else:
                logger.info("empty movie ads.")
        except:
             logger.error("err msg={}".format(traceback.format_exc()))
        return ""
 
    def get_all_ads(self):
        self.ads_datas = {}
        self.ads_datas_path = self.conf["ads"]
        if os.path.exists(self.ads_datas_path):
            self.ads_datas = read_pickle(self.ads_datas_path)
        rets = []
        for key in self.ads_datas:
            rets.append("{} ------ {}".format(key, self.ads_datas[key]))
        if len(rets) == 0:
            rets.append("暂无可用广告")
        return "\n".join(rets)

    # 额度查询
    def check_limit(self, e_context: EventContext):
        # 获取用户信息，进行充值
        reply = Reply()  # 创建回复消息对象
        reply.type = ReplyType.TEXT  # 设置回复消息的类型为文本
        user_id = self.userInfo['user_id']
        user_key = self.userInfo['user_key']
        user_name = self.userInfo['user_nickname']
        limit = self.user_datas[user_key]['limit']
        if limit <= 5:
            reply.content = "您当前剩余额度{}次, 请及时联系群主充值.".format(self.user_datas[user_key]['limit'])
        else:
            reply.content = "您当前剩余额度{}次.".format(self.user_datas[user_key]['limit'])
        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS

    def is_new_search_word(self, search_words, movie_name):
        is_new = True
        set_movie_name = set(movie_name)
        for word in search_words:
            set_word = set(word)
            common_chars = set_movie_name.intersection(set_word)
            if len(common_chars)*1.0  / (len(set_movie_name) + 0.1) > 0.6:
                is_new = False
                break
        return is_new

    def get_help_text(self, **kwargs):
        help_text = "发送关键词执行对应操作\n"
        help_text += "输入 '电影更新'， 将获取今日更新的电影\n"
        help_text += "输入 '找三体'， 将获取三体资源\n"
        help_text += "输入 '加入资源白名单+资源名'， 将资源加入到白名单中\n"
        help_text += "输入 '开启广告'，开启广告信息\n"
        help_text += "输入 '关闭广告'，关闭广告信息\n"
        help_text += "输入 '添加广告+广告内容'，加入广告信息\n"
        help_text += "输入 '删除广告+广告ID'，删除广告信息\n"
        help_text += "输入 '固定广告+广告ID'，删除广告信息\n"
        help_text += "输入 '所有广告'，获取所有广告信息\n"
        return help_text
