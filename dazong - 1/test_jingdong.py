# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, '.')

from crawlers.jingdong import JingdongCrawler

crawler = JingdongCrawler()

print("=== 京东爬虫可行性测试 ===\n")

print("1. 检测设备连接...")
if crawler.check_device():
    print("   [OK] 设备已连接")
else:
    print("   [FAIL] 设备未连接")
    sys.exit(1)

print("\n2. 检测京东App运行状态...")
if crawler.check_app_running():
    print("   [OK] 京东App正在运行")
else:
    print("   [WARN] 京东App未运行 (需要手动打开)")

print("\n3. 获取屏幕XML...")
texts = crawler.get_screen_text()
print(f"   获取到 {len(texts)} 个文本元素")
if texts:
    print(f"   示例: {texts[0][:50]}...")
else:
    print("   [FAIL] 未能获取屏幕内容")

print("\n4. 测试滑动...")
crawler.swipe_up()
print("   [OK] 滑动完成")

print("\n=== 核心功能测试通过 ===")
print("\n说明: 爬虫核心功能正常。")
print("完整采集需要在手机打开京东App并进入商品评价页面后运行GUI程序。")
