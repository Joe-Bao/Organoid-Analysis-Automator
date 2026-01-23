import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
import time
import sys

# --- 全局外观设置 ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue") 

class ORGANOIDApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. 基础窗口配置
        self.title("ORGANOID Automator v0.2 - Development Edition")
        self.geometry("1000x650")
        
        if getattr(sys, 'frozen', False):
            # in release env
            self.project_root = os.path.dirname(sys.executable)
        else:
            # In dev env
            self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._setup_sidebar()
        self._setup_main_area()

    def _setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="ORGANOID \nAutomator", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        self.btn_dashboard = ctk.CTkButton(self.sidebar_frame, text=" Dashboard", command=lambda: self.tabview.set("Dashboard"), height=40, anchor="w", font=ctk.CTkFont(size=14))
        self.btn_dashboard.grid(row=1, column=0, padx=20, pady=10)

        self.btn_settings = ctk.CTkButton(self.sidebar_frame, text=" Settings", command=lambda: self.tabview.set("Settings"), height=40, anchor="w", font=ctk.CTkFont(size=14), fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        self.btn_settings.grid(row=2, column=0, padx=20, pady=10)

        self.version_label = ctk.CTkLabel(self.sidebar_frame, text="v0.2 Dev\nMIT License", text_color="gray", font=ctk.CTkFont(size=10))
        self.version_label.grid(row=5, column=0, padx=20, pady=20)

    def _setup_main_area(self):
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.tab_dashboard = self.tabview.add("Dashboard")
        self.tab_settings = self.tabview.add("Settings")

        self._build_dashboard_tab()
        self._build_settings_tab()

    def _build_dashboard_tab(self):
        # 1. 源文件
        self.frame_src = ctk.CTkFrame(self.tab_dashboard)
        self.frame_src.pack(fill="x", padx=10, pady=(10, 0))
        self.lbl_src = ctk.CTkLabel(self.frame_src, text="Source Images Directory:", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_src.pack(anchor="w", padx=15, pady=(10, 5))
        self.entry_src = ctk.CTkEntry(self.frame_src, placeholder_text="Select the folder containing raw images...")
        self.entry_src.pack(side="left", fill="x", expand=True, padx=(15, 10), pady=10)
        self.btn_browse = ctk.CTkButton(self.frame_src, text="Browse...", width=100, command=self.browse_folder)
        self.btn_browse.pack(side="right", padx=(0, 15), pady=10)

        # 2. 参数
        self.frame_params = ctk.CTkFrame(self.tab_dashboard)
        self.frame_params.pack(fill="x", padx=10, pady=10)
        self.lbl_thresh = ctk.CTkLabel(self.frame_params, text="Filter Threshold (Min Sqrt Area):", font=ctk.CTkFont(size=14, weight="bold"))
        self.lbl_thresh.pack(side="left", padx=15, pady=20)
        self.entry_thresh = ctk.CTkEntry(self.frame_params, width=120, justify="center")
        self.entry_thresh.insert(0, "0.0")
        self.entry_thresh.pack(side="left", padx=10)

        # 3. 启动按钮
        self.btn_run = ctk.CTkButton(self.tab_dashboard, text="🚀 INITIALIZE PIPELINE", font=ctk.CTkFont(size=16, weight="bold"), height=50, fg_color="#2CC985", hover_color="#229A65", command=self.start_pipeline_thread)
        self.btn_run.pack(fill="x", padx=10, pady=10)

        # 4. 进度条
        self.progress_bar = ctk.CTkProgressBar(self.tab_dashboard)
        self.progress_bar.pack(fill="x", padx=10, pady=(10, 5))
        self.progress_bar.set(0)

        # 5. 日志
        self.lbl_log = ctk.CTkLabel(self.tab_dashboard, text="System Logs:", font=ctk.CTkFont(weight="bold"))
        self.lbl_log.pack(anchor="w", padx=10, pady=(5, 0))
        self.log_box = ctk.CTkTextbox(self.tab_dashboard, font=("Consolas", 11))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.log_box.configure(state="disabled")

    def _build_settings_tab(self):
        ctk.CTkLabel(self.tab_settings, text="Engine Configuration", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        self.sw_gpu = ctk.CTkSwitch(self.tab_settings, text="Enable CUDA Acceleration (GPU)")
        self.sw_gpu.select()
        self.sw_gpu.pack(pady=10)
        self.sw_clean = ctk.CTkSwitch(self.tab_settings, text="Auto-Cleanup Intermediate CSVs")
        self.sw_clean.pack(pady=10)
        self.sw_debug = ctk.CTkSwitch(self.tab_settings, text="Verbose Debug Mode")
        self.sw_debug.pack(pady=10)

    # --- 交互逻辑 ---

    def browse_folder(self):
        # 使用 update() 强制刷新 UI 事件，减少卡死概率
        self.update()
        f = filedialog.askdirectory(title="Select Image Folder")
        if f: 
            self.entry_src.delete(0, "end")
            self.entry_src.insert(0, f)

    def log_message(self, msg):
        try:
            timestamp = time.strftime('%H:%M:%S')
            full_msg = f"[{timestamp}] {msg}\n"
            self.log_box.configure(state="normal")
            self.log_box.insert("end", full_msg)
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        except Exception as e:
            print(f"Log Error: {e}")

    def start_pipeline_thread(self):
        """主线程：负责检查参数、锁定 UI、启动子线程"""
        src = self.entry_src.get()
        if not src: 
            messagebox.showwarning("Input Error", "Please select a source directory.")
            return
        
        try:
            thresh = float(self.entry_thresh.get() or 0)
        except ValueError:
            messagebox.showerror("Format Error", "Threshold must be a number.")
            return

        # 锁定 UI
        self.btn_run.configure(state="disabled", text="INITIALIZING...")
        self.progress_bar.configure(mode="indeterminate")
        self.progress_bar.start()

        # 启动线程，目标指向 _run_pipeline_wrapper
        threading.Thread(target=self._run_pipeline_wrapper, args=(src, thresh), daemon=True).start()

    def _run_pipeline_wrapper(self, src, thresh):
        """
        子线程：负责导入 heavy 模块并运行业务逻辑
        """
        try:
            # CRITICAL FIX: Lazy Import Strategy
            # We MUST import PipelineManager (and pywinauto) here, inside the thread,
            # rather than at the top level of the file.
            #
            # Reason: Top-level import triggers pywinauto's UIA/COM initialization immediately.
            # This creates a conflict with Tkinter's main loop and file dialogs, causing
            # the application to freeze (deadlock) when the "Browse" button is clicked.
            from src.core.automation import PipelineManager
            
            # 实例化并运行
            manager = PipelineManager(self.project_root, self.log_message)
            manager.run(src, thresh)
            
            self.log_message("✅ Task Finished.")

        except ImportError as e:
            self.log_message(f"❌ Dependency Error: Could not import core modules. {e}")
        except Exception as e:
            self.log_message(f"❌ Execution Error: {str(e)}")
        finally:
            # 无论成功还是失败，都必须重置 UI
            # 使用 self.after 将 UI 重置操作调度回主线程执行
            self.after(0, self._reset_ui_state)

    def _reset_ui_state(self):
        """重置 UI 状态 (在主线程执行)"""
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1.0)
        self.btn_run.configure(state="normal", text="🚀 INITIALIZE PIPELINE")

if __name__ == "__main__":
    app = ORGANOIDApp()
    app.mainloop()