# -*- coding: utf-8 -*-
from .dianping import DianpingCrawler
from .jingdong import JingdongCrawler

PLATFORMS = {
    "dianping": {
        "name": "大众点评",
        "class": DianpingCrawler,
        "icon": "🛒"
    },
    "jingdong": {
        "name": "京东",
        "class": JingdongCrawler,
        "icon": "🛍️"
    }
}

def get_crawler(platform_id):
    if platform_id in PLATFORMS:
        return PLATFORMS[platform_id]["class"]
    return None
