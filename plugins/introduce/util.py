#! coding: utf-8
import os
import re
import io
import json
import base64
import pickle
import requests
from PIL import Image
from plugins import *
from lib import itchat
from lib.itchat.content import *
from bridge.reply import Reply, ReplyType
from config import conf
from common.log import logger

def read_pickle(path):
    with open(path, "rb") as f:
        data = pickle.load(f)
    return data

def write_pickle(path, content):
    with open(path, "wb") as f:
        pickle.dump(content, f)
    return True

def img_to_jpeg(image_url):
    try:
        image = io.BytesIO()
        proxies = {}
        res = requests.get(image_url, proxies=proxies, stream=True)
        idata = Image.open(io.BytesIO(res.content))
        idata = idata.convert("RGB")
        idata.save(image, format="JPEG")
        return image
    except Exception as e:
        logger.error(e)
        return False

def send(reply, e_context: EventContext, reply_type=ReplyType.TEXT):
    if isinstance(reply, Reply):
        if not reply.type and reply_type:
            reply.type = reply_type
    else:
        reply = Reply(reply_type, reply)
    channel = e_context['channel']
    context = e_context['context']

    receiver_list = context.kwargs["receiver"].split(",")
    logger.info("receiver_list={}".format(receiver_list))
    for receiver in receiver_list:
        context.kwargs["receiver"] = receiver
        context.kwargs["session_id"] = receiver
        channel.send(reply, context)
        ## reply的包装步骤
        #rd = channel._decorate_reply(context, reply)
        # reply的发送步骤
        #channel._send_reply(context, rd)

def send2(reply, e_context: EventContext, reply_type=ReplyType.TEXT, action=EventAction.BREAK_PASS):
    if isinstance(reply, Reply):
        if not reply.type and reply_type:
            reply.type = reply_type
    else:
        reply = Reply(reply_type, reply)
    e_context["reply"] = reply
    e_context.action = action
