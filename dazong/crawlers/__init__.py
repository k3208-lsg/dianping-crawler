# -*- coding: utf-8 -*-
from .dianping import DianpingCrawler

PLATFORMS = {
    "dianping": {
        "name": "大众点评",
        "class": DianpingCrawler,
        "icon": "🛒"
    }
}

def get_crawler(platform_id):
    if platform_id in PLATFORMS:
        return PLATFORMS[platform_id]["class"]
    return None
