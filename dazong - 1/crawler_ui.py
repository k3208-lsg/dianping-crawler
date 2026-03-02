# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import queue

from crawlers import PLATFORMS, get_crawler

ADB_PATH = r"C:\Users\kkk\Downloads\platform-tools\adb.exe"
DEVICE_ID = "10AF4U13UD001JH"

class CuteCrawlerUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("评论小狐狸 v1.0")
        self.root.geometry("520x720")
        self.root.resizable(False, False)
        self.root.configure(bg="#FFF5EE")
        
        self.is_running = False
        self.crawler = None
        self.log_queue = queue.Queue()
        
        self.setup_ui()
        self.update_log()
        
    def setup_ui(self):
        title_frame = tk.Frame(self.root, bg="#FFF5EE")
        title_frame.pack(pady=10)
        
        title_label = tk.Label(
            title_frame, 
            text="评论采集小助手",
            font=("Microsoft YaHei", 18, "bold"),
            fg="#FF6B6B",
            bg="#FFF5EE"
        )
        title_label.pack()
        
        subtitle = tk.Label(
            title_frame,
            text="~ 帮你轻松抓取评论数据 ~",
            font=("Microsoft YaHei", 10),
            fg="#999999",
            bg="#FFF5EE"
        )
        subtitle.pack()
        
        btn_frame = tk.Frame(self.root, bg="#FFF5EE")
        btn_frame.pack(pady=15)
        
        self.start_btn = tk.Button(
            btn_frame,
            text="开始采集",
            font=("Microsoft YaHei", 14, "bold"),
            bg="#FF6B6B",
            fg="white",
            width=14,
            height=2,
            relief="flat",
            cursor="hand2",
            command=self.start_crawl
        )
        self.start_btn.pack(side="left", padx=8)
        
        self.stop_btn = tk.Button(
            btn_frame,
            text="停止",
            font=("Microsoft YaHei", 14, "bold"),
            bg="#CCCCCC",
            fg="white",
            width=14,
            height=2,
            relief="flat",
            cursor="hand2",
            command=self.stop_crawl,
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=8)
        
        self.check_device_btn = tk.Button(
            btn_frame,
            text="检测设备",
            font=("Microsoft YaHei", 14, "bold"),
            bg="#4ECDC4",
            fg="white",
            width=14,
            height=2,
            relief="flat",
            cursor="hand2",
            command=self.check_device
        )
        self.check_device_btn.pack(side="left", padx=8)
        
        platform_frame = tk.LabelFrame(
            self.root, 
            text="选择平台", 
            font=("Microsoft YaHei", 10, "bold"),
            fg="#FF6B6B",
            bg="#FFF5EE",
            padx=15,
            pady=8
        )
        platform_frame.pack(fill="x", padx=20, pady=8)
        
        self.platform_var = tk.StringVar(value="dianping")
        
        for platform_id, info in PLATFORMS.items():
            rb = tk.Radiobutton(
                platform_frame,
                text=f"{info['icon']} {info['name']}",
                variable=self.platform_var,
                value=platform_id,
                font=("Microsoft YaHei", 11),
                bg="#FFF5EE",
                fg="#333333",
                selectcolor="#FFE4E1",
                activebackground="#FFF5EE"
            )
            rb.pack(anchor="w", pady=2)
        
        count_frame = tk.LabelFrame(
            self.root,
            text="采集数量",
            font=("Microsoft YaHei", 10, "bold"),
            fg="#FF6B6B",
            bg="#FFF5EE",
            padx=15,
            pady=8
        )
        count_frame.pack(fill="x", padx=20, pady=8)
        
        count_inner = tk.Frame(count_frame, bg="#FFF5EE")
        count_inner.pack(fill="x")
        
        tk.Label(
            count_inner,
            text="目标条数:",
            font=("Microsoft YaHei", 10),
            bg="#FFF5EE"
        ).pack(side="left")
        
        self.count_var = tk.StringVar(value="1000")
        self.count_entry = tk.Entry(
            count_inner,
            textvariable=self.count_var,
            font=("Microsoft YaHei", 12),
            width=10,
            justify="center"
        )
        self.count_entry.pack(side="left", padx=10)
        
        tk.Label(
            count_inner,
            text="条",
            font=("Microsoft YaHei", 10),
            bg="#FFF5EE"
        ).pack(side="left")
        
        self.status_frame = tk.LabelFrame(
            self.root,
            text="运行状态",
            font=("Microsoft YaHei", 10, "bold"),
            fg="#FF6B6B",
            bg="#FFF5EE",
            padx=15,
            pady=8
        )
        self.status_frame.pack(fill="x", padx=20, pady=8)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="等待开始...",
            font=("Microsoft YaHei", 11),
            bg="#FFF5EE",
            fg="#666666"
        )
        self.status_label.pack()
        
        self.progress_var = tk.StringVar(value="已采集: 0 / 0")
        self.progress_label = tk.Label(
            self.status_frame,
            textvariable=self.progress_var,
            font=("Microsoft YaHei", 10),
            bg="#FFF5EE",
            fg="#999999"
        )
        self.progress_label.pack(pady=3)
        
        self.progress_bar = ttk.Progressbar(
            self.status_frame,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(pady=3)
        
        tip_frame = tk.LabelFrame(
            self.root,
            text="温馨提示",
            font=("Microsoft YaHei", 10, "bold"),
            fg="#FF6B6B",
            bg="#FFF5EE",
            padx=15,
            pady=8
        )
        tip_frame.pack(fill="x", padx=20, pady=8)
        
        self.tip_label = tk.Label(
            tip_frame,
            text="准备好后点击开始按钮哦~",
            font=("Microsoft YaHei", 9),
            bg="#FFF5EE",
            fg="#666666",
            wraplength=400,
            justify="left"
        )
        self.tip_label.pack(anchor="w")
        
        log_frame = tk.LabelFrame(
            self.root,
            text="运行日志",
            font=("Microsoft YaHei", 10, "bold"),
            fg="#FF6B6B",
            bg="#FFF5EE",
            padx=10,
            pady=5
        )
        log_frame.pack(fill="both", expand=True, padx=20, pady=8)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=6,
            font=("Consolas", 9),
            bg="#FFFAF0",
            fg="#333333"
        )
        self.log_text.pack(fill="both", expand=True)
        
    def log(self, message):
        self.log_queue.put(message)
        
    def update_log(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                timestamp = time.strftime("%H:%M:%S")
                self.log_text.insert("end", f"[{timestamp}] {msg}\n")
                self.log_text.see("end")
        except:
            pass
        self.root.after(100, self.update_log)
        
    def update_status(self, text, color="#666666"):
        self.root.after(0, lambda: self.status_label.config(text=text, fg=color))
        
    def update_tip(self, text):
        self.root.after(0, lambda: self.tip_label.config(text=text))
        
    def update_progress(self, current, total):
        percent = (current / total * 100) if total > 0 else 0
        self.root.after(0, lambda: self.progress_var.set(f"已采集: {current} / {total}"))
        self.root.after(0, lambda: setattr(self.progress_bar, 'value', percent))
        
    def check_device(self):
        self.log("正在检测设备...")
        import subprocess
        full_cmd = f'"{ADB_PATH}" -s {DEVICE_ID} devices'
        result = subprocess.run(full_cmd, shell=True, capture_output=True)
        output = result.stdout.decode('utf-8', errors='ignore')
        
        if DEVICE_ID in output and "device" in output:
            self.log(f"设备已连接: {DEVICE_ID}")
            messagebox.showinfo("设备检测", f"设备已连接!\n\n设备ID: {DEVICE_ID}")
        else:
            self.log("设备未连接")
            messagebox.showwarning("设备检测", "设备未连接\n\n请检查:\n1. USB线是否连接\n2. USB调试是否开启\n3. 是否授权此电脑")
            
    def show_action_dialog(self, platform_name):
        dialog = tk.Toplevel(self.root)
        dialog.title("需要您的操作")
        dialog.geometry("420x300")
        dialog.configure(bg="#FFF5EE")
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.geometry(f"+{self.root.winfo_x() + 40}+{self.root.winfo_y() + 80}")
        
        tk.Label(
            dialog,
            text="需要您的操作",
            font=("Microsoft YaHei", 14, "bold"),
            fg="#FF6B6B",
            bg="#FFF5EE"
        ).pack(pady=15)
        
        message = f"请在手机上完成以下操作:\n\n1. 打开 {platform_name} App\n2. 搜索目标商家\n3. 进入商家详情页\n4. 点击进入评论页面\n\n完成后点击下方按钮"
        
        msg_label = tk.Label(
            dialog,
            text=message,
            font=("Microsoft YaHei", 10),
            bg="#FFF5EE",
            fg="#333333",
            wraplength=380,
            justify="left"
        )
        msg_label.pack(pady=10, padx=20)
        
        countdown_var = tk.StringVar(value="倒计时: 30 秒")
        countdown_label = tk.Label(
            dialog,
            textvariable=countdown_var,
            font=("Microsoft YaHei", 16, "bold"),
            fg="#FF6B6B",
            bg="#FFF5EE"
        )
        countdown_label.pack(pady=10)
        
        done = [False]
        cancelled = [False]
        
        def on_done():
            done[0] = True
            dialog.destroy()
            
        def on_cancel():
            cancelled[0] = True
            dialog.destroy()
            
        btn_frame = tk.Frame(dialog, bg="#FFF5EE")
        btn_frame.pack(pady=10)
        
        done_btn = tk.Button(
            btn_frame,
            text="我已完成",
            font=("Microsoft YaHei", 11, "bold"),
            bg="#4ECDC4",
            fg="white",
            width=12,
            height=2,
            relief="flat",
            cursor="hand2",
            command=on_done
        )
        done_btn.pack(side="left", padx=10)
        
        cancel_btn = tk.Button(
            btn_frame,
            text="取消",
            font=("Microsoft YaHei", 11, "bold"),
            bg="#CCCCCC",
            fg="white",
            width=12,
            height=2,
            relief="flat",
            cursor="hand2",
            command=on_cancel
        )
        cancel_btn.pack(side="left", padx=10)
        
        for i in range(30, 0, -1):
            if done[0] or cancelled[0]:
                break
            countdown_var.set(f"倒计时: {i} 秒")
            dialog.update()
            time.sleep(1)
            
        if not done[0] and not cancelled[0]:
            dialog.destroy()
            return True
            
        return done[0] and not cancelled[0]
    
    def crawl_thread(self):
        platform_id = self.platform_var.get()
        target_count = int(self.count_var.get())
        
        crawler_class = get_crawler(platform_id)
        if not crawler_class:
            self.log(f"未知平台: {platform_id}")
            self.finish_crawl()
            return
            
        self.crawler = crawler_class(
            on_log=self.log,
            on_progress=self.update_progress,
            on_status=self.update_status,
            on_tip=self.update_tip
        )
        
        def wait_callback():
            return self.show_action_dialog(self.crawler.PLATFORM_NAME)
            
        success = self.crawler.crawl(target_count, wait_callback)
        
        if success and self.crawler.comments:
            count = len(self.crawler.comments)
            self.update_status(f"采集完成! 共 {count} 条", "#4ECDC4")
            self.update_tip(f"采集完成!\n\n共获取 {count} 条评论\n数据已保存到 data/{platform_id}/ 文件夹")
            self.root.after(0, lambda: messagebox.showinfo("完成", f"采集完成!\n\n共获取 {count} 条评论\n数据已保存到 data/{platform_id}/ 文件夹"))
        elif self.is_running:
            self.update_status("采集结束", "#999999")
            self.update_tip("未能获取数据，请检查:\n\n1. 手机是否在评论页面\n2. App是否正常显示")
            
        self.finish_crawl()
        
    def start_crawl(self):
        try:
            target = int(self.count_var.get())
            if target <= 0:
                raise ValueError
        except:
            messagebox.showwarning("提示", "请输入有效的采集数量!")
            return
            
        self.is_running = True
        
        self.start_btn.config(state="disabled", bg="#CCCCCC")
        self.stop_btn.config(state="normal", bg="#FF6B6B")
        self.check_device_btn.config(state="disabled")
        self.count_entry.config(state="disabled")
        
        self.update_progress(0, target)
        
        thread = threading.Thread(target=self.crawl_thread, daemon=True)
        thread.start()
        
    def stop_crawl(self):
        self.is_running = False
        if self.crawler:
            self.crawler.stop()
        self.log("用户停止采集")
        
    def finish_crawl(self):
        self.is_running = False
        self.root.after(0, lambda: self.start_btn.config(state="normal", bg="#FF6B6B"))
        self.root.after(0, lambda: self.stop_btn.config(state="disabled", bg="#CCCCCC"))
        self.root.after(0, lambda: self.check_device_btn.config(state="normal"))
        self.root.after(0, lambda: self.count_entry.config(state="normal"))
            
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CuteCrawlerUI()
    app.run()
