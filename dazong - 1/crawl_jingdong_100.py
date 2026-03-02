# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

from crawlers.jingdong import JingdongCrawler

def log(msg):
    print(f"[LOG] {msg}")

def progress(current, total):
    print(f"[进度] {current}/{total}")

def status(text, color="#666666"):
    print(f"[状态] {text}")

def tip(text):
    print(f"[提示] {text}")

crawler = JingdongCrawler(
    on_log=log,
    on_progress=progress,
    on_status=status,
    on_tip=tip
)

print("=== 京东评论采集测试 (目标100条) ===\n")
print("直接开始采集...\n")
result = crawler.crawl(target_count=100, wait_callback=lambda: True)

if result:
    total = len(crawler.comments)
    print(f"\n=== 采集完成 ===")
    print(f"共采集 {total} 条评论")
    print(f"数据保存位置: data/jingdong/")
else:
    print("\n采集失败")
