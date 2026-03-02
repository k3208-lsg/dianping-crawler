# -*- coding: utf-8 -*-
import subprocess
import time
import csv
import os
import re
from datetime import datetime
from xml.etree import ElementTree

ADB_PATH = r"C:\Users\kkk\Downloads\platform-tools\adb.exe"
DEVICE_ID = "10AF4U13UD001JH"

JUNK_PATTERNS = [
    r'^jd_[a-z0-9]{8,}$',
    r'^京东手机数码-',
    r'^上海\d+区',
    r'^已购\s+\S+\s+\d+GB$',
    r'^已购\s+\S+\s+\d+TB$',
    r'^已购\s+\S+色\s+\d+GB$',
    r'^已购\s+\S+色\s+\d+TB$',
    r'^已购\s+\S+\s+\d+GB\s+\S+$',
    r'^已购\s+\S+\s+\d+TB\s+\S+$',
    r'^AI全网评',
    r'^京东鼓励真实',
    r'^您对评价的使用体验',
    r'^7天无理由退货',
    r'^\S+旗舰店$',
    r'^[A-Za-z0-9_]{3,20}$',
    r'^\S+专营店$',
]

JUNK_KEYWORDS = [
    "京东手机数码",
    "上海市宝山区",
    "上海市宝山区沪太路",
    "京东家电",
    "手机专柜",
    "jd_",
    "京东鼓励",
    "您对评价",
    "7天无理由退货",
    "防伪签",
    "密封条损毁",
    "AI全网评",
]

class JingdongCrawler:
    PLATFORM_NAME = "京东"
    PLATFORM_ID = "jingdong"
    
    def __init__(self, on_log=None, on_progress=None, on_status=None, on_tip=None):
        self.on_log = on_log
        self.on_progress = on_progress
        self.on_status = on_status
        self.on_tip = on_tip
        
        self.comments = []
        self.seen_contents = set()
        self.is_running = False
        self.file_index = 1
        self.batch_size = 100
        self.saved_count = 0
        self.output_dir = f"data/{self.PLATFORM_ID}"
        
    def log(self, msg):
        if self.on_log:
            self.on_log(msg)
            
    def update_status(self, text, color="#666666"):
        if self.on_status:
            self.on_status(text, color)
            
    def update_progress(self, current, total):
        if self.on_progress:
            self.on_progress(current, total)
            
    def update_tip(self, text):
        if self.on_tip:
            self.on_tip(text)
    
    def adb_cmd(self, cmd):
        full_cmd = f'"{ADB_PATH}" -s {DEVICE_ID} {cmd}'
        result = subprocess.run(full_cmd, shell=True, capture_output=True)
        return result.stdout.decode('utf-8', errors='ignore')
    
    def check_device(self):
        result = self.adb_cmd("devices")
        return DEVICE_ID in result and "device" in result
    
    def check_app_running(self):
        result = self.adb_cmd("shell dumpsys activity activities")
        return "com.jingdong.app.mall" in result
    
    def swipe_up(self):
        self.adb_cmd("shell input swipe 540 1800 540 500 600")
        time.sleep(1.5)
    
    def click_expand(self):
        self.adb_cmd("shell uiautomator dump /sdcard/ui.xml")
        time.sleep(0.3)
        xml_output = self.adb_cmd("shell cat /sdcard/ui.xml")
        try:
            if not xml_output or not xml_output.strip().startswith('<'):
                return False
            root = ElementTree.fromstring(xml_output[:500000])
            for elem in root.iter():
                text = elem.attrib.get('text', '')
                if '展开' in text and len(text) < 20:
                    bounds = elem.attrib.get('bounds', '')
                    if bounds:
                        match = re.findall(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
                        if match:
                            x = (int(match[0][0]) + int(match[0][2])) // 2
                            y = (int(match[0][1]) + int(match[0][3])) // 2
                            self.adb_cmd(f"shell input tap {x} {y}")
                            time.sleep(0.8)
                            return True
            return False
        except:
            return False
        
    def is_junk(self, text):
        if not text or len(text.strip()) < 15:
            return True
        text = text.strip()
        for pattern in JUNK_PATTERNS:
            if re.match(pattern, text, re.IGNORECASE):
                return True
        for keyword in JUNK_KEYWORDS:
            if text.startswith(keyword):
                return True
        return False
    
    def clean_text(self, text):
        text = text.replace('... 展开', '').replace('…展开', '').replace(' 展开', '')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
        
    def get_screen_text(self):
        self.adb_cmd("shell uiautomator dump /sdcard/ui.xml")
        time.sleep(0.3)
        xml_output = self.adb_cmd("shell cat /sdcard/ui.xml")
        try:
            if not xml_output or not xml_output.strip().startswith('<'):
                return []
            root = ElementTree.fromstring(xml_output[:500000])
            texts = []
            for elem in root.iter():
                text = elem.attrib.get('text', '').strip()
                text = self.clean_text(text)
                if text and not self.is_junk(text):
                    texts.append(text)
            return texts
        except:
            return []
    
    def save_batch(self, force=False):
        if not self.comments:
            return []
            
        os.makedirs(self.output_dir, exist_ok=True)
        
        saved_files = []
        start_idx = self.saved_count
        
        while start_idx < len(self.comments):
            end_idx = min(start_idx + self.batch_size, len(self.comments))
            batch = self.comments[start_idx:end_idx]
            
            if len(batch) < self.batch_size and not force:
                break
                
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.output_dir}/comments_part{self.file_index}_{timestamp}.csv"
            
            with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=['content', 'crawl_time'])
                writer.writeheader()
                writer.writerows(batch)
                
            saved_files.append(filename)
            self.log(f"💾 保存第 {self.file_index} 批: {len(batch)} 条")
            
            self.file_index += 1
            self.saved_count = end_idx
            start_idx = end_idx
            
        return saved_files
    
    def stop(self):
        self.is_running = False
        
    def crawl(self, target_count, wait_callback=None):
        self.comments = []
        self.seen_contents = set()
        self.is_running = True
        self.file_index = 1
        self.saved_count = 0
        
        self.log("🔍 检测设备连接...")
        if not self.check_device():
            self.update_status("❌ 设备未连接", "#FF0000")
            self.log("❌ 设备未连接")
            return False
            
        self.log("✅ 设备已连接")
        
        if not self.check_app_running():
            self.log(f"⚠️ 未检测到{self.PLATFORM_NAME}App在前台")
            
        self.update_status("⏳ 等待用户操作...", "#FF9500")
        self.update_tip(f"📱 请在手机上完成以下操作:\n\n1. 打开{self.PLATFORM_NAME}App\n2. 搜索目标商品\n3. 进入商品详情页\n4. 点击进入评价页面")
        
        self.log("📱 等待用户完成手机操作...")
        
        if wait_callback:
            if not wait_callback():
                return False
                
        if not self.is_running:
            return False
            
        self.update_status("🔄 正在采集...", "#4ECDC4")
        self.update_tip("🦊 小狐狸正在努力工作中...\n请保持手机屏幕常亮，不要切换App")
        
        self.log("🚀 开始采集评论...")
        self.update_progress(0, target_count)
        
        consecutive_empty = 0
        swipe_count = 0
        max_empty_count = 30
        last_count = 0
        expand_clicks = 0
        
        while self.is_running and len(self.comments) < target_count:
            self.click_expand()
            texts = self.get_screen_text()
            
            added = 0
            for text in texts:
                key = text[:50]
                if key not in self.seen_contents:
                    self.seen_contents.add(key)
                    self.comments.append({
                        'content': text,
                        'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    })
                    added += 1
                    
            if added > 0:
                consecutive_empty = 0
                last_count = len(self.comments)
                self.log(f"✨ 新增 {added} 条，共 {len(self.comments)} 条")
                self.update_progress(len(self.comments), target_count)
            else:
                consecutive_empty += 1
                
                if consecutive_empty > 10 and len(self.comments) > last_count:
                    self.log(f"⚠️ 网络可能卡顿，等待2秒后重试...")
                    time.sleep(2)
                    consecutive_empty -= 5
                
                if consecutive_empty >= max_empty_count:
                    self.log(f"⚠️ 连续{max_empty_count}次无新数据，已到底部")
                    break
            
            self.swipe_up()
            swipe_count += 1
            
            if swipe_count % 5 == 0:
                self.log(f"📱 已滑动 {swipe_count} 次，展开按钮点击 {expand_clicks} 次")
            
            if len(self.comments) - self.saved_count >= self.batch_size:
                self.save_batch()
                    
        if self.is_running:
            self.save_batch(force=True)
                
        return True
