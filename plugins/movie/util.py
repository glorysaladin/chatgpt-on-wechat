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
    data = {}
    if os.path.getsize(path) > 0:
        with open(path, "rb") as f:
            data = pickle.load(f)
    return data

def write_pickle(path, content):
    with open(path, "wb") as f:
        pickle.dump(content, f)
    return True
