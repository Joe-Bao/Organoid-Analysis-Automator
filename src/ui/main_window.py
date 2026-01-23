import customtkinter
# Disable automatic DPI awareness to prevent 
# "Can't find filter element" errors during Windows API initialization.
customtkinter.deactivate_automatic_dpi_awareness() 
import customtkinter as ctk
from src.core.automation import PipelineManager
from tkinter import filedialog, messagebox
import threading
import os
import time
import sys



# --- 全局外观设置 ---
ctk.set_appearance_mode("System")  # 模式: "System" (跟随系统)
ctk.set_default_color_theme("dark-blue") 

class BioQuantApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. 基础窗口配置
        self.title("ORGANOID Automator v0.1 - Development Edition")
        self.geometry("1000x650")
        
        # 动态获取项目根目录 (假设此文件在 src/ui/ 下，回退两级到根目录)
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        
        # 2. 网格布局配置 (1行2列)
        # column 0 = 侧边栏 (固定宽度)
        # column 1 = 主内容区 (自适应)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 3. 初始化 UI 组件
        self._setup_sidebar()
        self._setup_main_area()

    def _setup_sidebar(self):
        """左侧侧边栏布局"""
        self.sidebar_frame = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1) # 让版本号沉底

        # Logo / 标题
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="BioQuant\nAutomator", 
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        # 导航按钮
        self.btn_dashboard = ctk.CTkButton(
            self.sidebar_frame, 
            text=" Dashboard", 
            command=lambda: self.tabview.set("Dashboard"),
            height=40,
            anchor="w",
            font=ctk.CTkFont(size=14)
        )
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        self.btn_settings = ctk.CTkButton(
            self.sidebar_frame, 
            text=" Settings", 
            command=lambda: self.tabview.set("Settings"),
            height=40,
            anchor="w",
            font=ctk.CTkFont(size=14),
            fg_color="transparent", 
            border_width=2, 
            text_color=("gray10", "#DCE4EE")
        )
        self.btn_settings.grid(row=2, column=0, padx=20, pady=10)

        # 底部版本信息
        self.version_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="v1.0.0 Dev\nMIT License", 
            text_color="gray",
            font=ctk.CTkFont(size=10)
        )
        self.version_label.grid(row=5, column=0, padx=20, pady=20)

    def _setup_main_area(self):
        """右侧主内容区 (Tabview)"""
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # 创建标签页
        self.tab_dashboard = self.tabview.add("Dashboard")
        self.tab_settings = self.tabview.add("Settings")

        self._build_dashboard_tab()
        self._build_settings_tab()

    def _build_dashboard_tab(self):
        """构建仪表盘页面"""
        # --- 1. 源文件选择区域 ---
        self.frame_src = ctk.CTkFrame(self.tab_dashboard)
        self.frame_src.pack(fill="x", padx=10, pady=(10, 0))

        self.lbl_src = ctk.CTkLabel(
            self.frame_src, 
            text="Source Images Directory:", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_src.pack(anchor="w", padx=15, pady=(10, 5))

        self.entry_src = ctk.CTkEntry(
            self.frame_src, 
            placeholder_text="Select the folder containing raw images..."
        )
        self.entry_src.pack(side="left", fill="x", expand=True, padx=(15, 10), pady=10)

        self.btn_browse = ctk.CTkButton(
            self.frame_src, 
            text="Browse...", 
            width=100, 
            command=self.browse_folder
        )
        self.btn_browse.pack(side="right", padx=(0, 15), pady=10)

        # --- 2. 参数设置区域 ---
        self.frame_params = ctk.CTkFrame(self.tab_dashboard)
        self.frame_params.pack(fill="x", padx=10, pady=10)

        self.lbl_thresh = ctk.CTkLabel(
            self.frame_params, 
            text="Filter Threshold (Min Sqrt Area):", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_thresh.pack(side="left", padx=15, pady=20)

        self.entry_thresh = ctk.CTkEntry(self.frame_params, width=120, justify="center")
        self.entry_thresh.insert(0, "0.0")
        self.entry_thresh.pack(side="left", padx=10)

        # --- 3. 启动按钮 ---
        self.btn_run = ctk.CTkButton(
            self.tab_dashboard, 
            text="🚀 INITIALIZE PIPELINE", 
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color="#2CC985", 
            hover_color="#229A65",
            command=self.start_pipeline_thread
        )
        self.btn_run.pack(fill="x", padx=10, pady=10)

        # --- 4. 进度条与状态 ---
        self.progress_bar = ctk.CTkProgressBar(self.tab_dashboard)
        self.progress_bar.pack(fill="x", padx=10, pady=(10, 5))
        self.progress_bar.set(0) # 0.0 到 1.0

        # --- 5. 日志控制台 ---
        self.lbl_log = ctk.CTkLabel(self.tab_dashboard, text="System Logs:", font=ctk.CTkFont(weight="bold"))
        self.lbl_log.pack(anchor="w", padx=10, pady=(5, 0))

        self.log_box = ctk.CTkTextbox(self.tab_dashboard, font=("Consolas", 11))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_box.configure(state="disabled")

    def _build_settings_tab(self):
        """构建设置页面 (增加专业感，暂未连接真实逻辑)"""
        ctk.CTkLabel(
            self.tab_settings, 
            text="Engine Configuration", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=20)

        self.sw_gpu = ctk.CTkSwitch(self.tab_settings, text="Enable CUDA Acceleration (GPU)")
        self.sw_gpu.select()
        self.sw_gpu.pack(pady=10)

        self.sw_clean = ctk.CTkSwitch(self.tab_settings, text="Auto-Cleanup Intermediate CSVs")
        self.sw_clean.pack(pady=10)

        self.sw_debug = ctk.CTkSwitch(self.tab_settings, text="Verbose Debug Mode")
        self.sw_debug.pack(pady=10)

    # --- 交互逻辑 ---

    def browse_folder(self):
        f = filedialog.askdirectory()
        if f: 
            self.entry_src.delete(0, "end")
            self.entry_src.insert(0, f)

    def log_message(self, msg):
        """
        回调函数：供 core 模块调用
        注意：Tkinter 非线程安全，虽然 CustomTkinter 处理得不错，
        但高并发下最好还是注意。这里直接插入即可。
        """
        try:
            timestamp = time.strftime('%H:%M:%S')
            full_msg = f"[{timestamp}] {msg}\n"
            
            self.log_box.configure(state="normal")
            self.log_box.insert("end", full_msg)
            self.log_box.see("end") # 自动滚动到底部
            self.log_box.configure(state="disabled")
        except Exception as e:
            print(f"Log Error: {e}")

    def start_pipeline_thread(self):
        # 1. 验证输入
        src = self.entry_src.get()
        if not src or not os.path.exists(src):
            messagebox.showerror("Input Error", "Please select a valid source directory.")
            return
        
        try:
            thresh = float(self.entry_thresh.get() or 0)
        except ValueError:
            messagebox.showerror("Input Error", "Threshold must be a number.")
            return

        # 2. 锁定 UI
        self.btn_run.configure(state="disabled", text="⏳ PIPELINE RUNNING...")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()
        
        # 3. 启动线程
        threading.Thread(target=self._run_pipeline_wrapper, args=(src, thresh), daemon=True).start()

    def _run_pipeline_wrapper(self, src, thresh):
        """
        线程目标函数：实例化 Manager 并运行
        """
        try:
            # 这里的 log_message 传给 manager，manager 会用它来发回日志
            manager = PipelineManager(self.project_root, self.log_message)
            manager.run(src, thresh)
            
            self.log_message("✅ Task Finished.")
        except Exception as e:
            self.log_message(f"❌ Thread Error: {str(e)}")
        finally:
            # 恢复 UI 状态 (需要回到主线程，Tkinter 中直接修改通常可以，严谨做法是用 after)
            self.after(0, self._reset_ui_state)

    def _reset_ui_state(self):
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1.0) # 进度条满
        self.btn_run.configure(state="normal", text="🚀 INITIALIZE PIPELINE")

if __name__ == "__main__":
    app = BioQuantApp()
    app.mainloop()