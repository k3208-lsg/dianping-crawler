# -*- coding: utf-8 -*-
import subprocess
import time
import csv
import os
from datetime import datetime
from xml.etree import ElementTree

ADB_PATH = r"C:\Users\kkk\Downloads\platform-tools\adb.exe"
DEVICE_ID = "10AF4U13UD001JH"

class DianpingCrawler:
    PLATFORM_NAME = "大众点评"
    PLATFORM_ID = "dianping"
    
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
        return "com.dianping.v1" in result
    
    def swipe_up(self):
        self.adb_cmd("shell input swipe 630 2000 630 600 500")
        time.sleep(1.5)
        
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
                if text and len(text) > 10:
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
        self.update_tip(f"📱 请在手机上完成以下操作:\n\n1. 打开{self.PLATFORM_NAME}App\n2. 搜索目标商家\n3. 进入商家详情页\n4. 点击进入评论页面")
        
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
        
        while self.is_running and len(self.comments) < target_count:
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
                self.log(f"✨ 新增 {added} 条，共 {len(self.comments)} 条")
                self.update_progress(len(self.comments), target_count)
            else:
                consecutive_empty += 1
                
            if consecutive_empty >= 10:
                self.log("⚠️ 连续10次无新数据，可能已到底部")
                break
                
            self.swipe_up()
            swipe_count += 1
            
            if len(self.comments) - self.saved_count >= self.batch_size:
                self.save_batch()
                    
        if self.is_running:
            self.save_batch(force=True)
                
        return True
