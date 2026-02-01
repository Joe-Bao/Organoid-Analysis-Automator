import os
import shutil
import time
import subprocess
import threading
from pywinauto.application import Application
from src.analysis.calculator import StatsCalculator # 调用计算层

class PipelineManager:
    def __init__(self, project_root, logger_callback):
        self.project_root = project_root
        self.log = logger_callback  # 这是一个函数，用来发消息给 UI
        
        # 关键路径定义 (相对于项目根目录)
        self.exe_dir = os.path.join(self.project_root, "GelNestOrganoidV3")
        self.exe_name = "GelNestOrganoidV3.exe"
        self.exe_path = os.path.join(self.exe_dir, self.exe_name)
        
        self.img_dir = os.path.join(self.exe_dir, "img")
        self.output_dir = os.path.join(self.exe_dir, "outputs")
        self.final_report = os.path.join(self.project_root, "ORGANOID_Final_Report.csv")

    def run(self, source_folder, threshold , confidence=0.82):
        """流水线主入口"""
        if not os.path.exists(self.exe_path):
            self.log(f"❌ Error: Executable not found at {self.exe_path}")
            self.log("👉 Please verify the 'GelNestOrganoidV3' folder structure.")
            return

        try:
            # 1. 环境准备
            self.log("🧹 Cleaning workspace...")
            self._prepare_directories()

            # 2. 搬运图片
            self.log(f"📦 Importing images from: {source_folder}")
            images = [f for f in os.listdir(source_folder) if f.lower().endswith(('.png', '.jpg', '.tif', '.bmp'))]
            if not images:
                self.log("⚠️ No images found in source folder.")
                return
            
            for img in images:
                shutil.copy2(os.path.join(source_folder, img), os.path.join(self.img_dir, img))
            self.log(f"✅ Imported {len(images)} images.")

            # 3. 启动 EXE (带 cwd 锁定)
            self.log(f"🚀 Launching {self.exe_name}...")
            # 关键：cwd 设置为 exe 所在目录，防止找不到 img
            process = subprocess.Popen(self.exe_path, cwd=self.exe_dir)
            
            # 4. 自动化点击
            self._automate_gui(confidence)

            # 5. 监控与计算
            self._monitor_results(len(images), threshold, process)

        except Exception as e:
            self.log(f"❌ Critical Error: {str(e)}")

    def _prepare_directories(self):
        if os.path.exists(self.img_dir): shutil.rmtree(self.img_dir)
        if os.path.exists(self.output_dir): shutil.rmtree(self.output_dir)
        os.makedirs(self.img_dir)
        os.makedirs(self.output_dir)

    def _automate_gui(self, confidence):
        self.log("🤖 Waiting for GUI...")
        try:
            app = Application(backend="uia").connect(path=self.exe_path, timeout=20)
            dlg = app.window(title_re=".*GelNestOrganoid.*")
            dlg.wait('visible', timeout=30)
            dlg.set_focus()
            time.sleep(1)
            
            # --- 步骤 0: 重置焦点 (点击左上角安全区) ---
            # 这一步是为了确保 Tab 计数是从“零”开始的
            self.log("⌨️ Focusing window...")
            dlg.click_input(coords=(20, 20)) # 点击左上角空白处，确保没有选中任何框
            time.sleep(0.5)

            # --- 步骤 1: 勾选免责声明 (Tab=2) ---
            # 你的测试：空白 -> Tab x2 -> Agree
            self.log("👆 Key-Nav: Toggling Disclaimer...")
            # 连续按 2 次 Tab，然后按空格键 (Space) 勾选
            dlg.type_keys("{TAB 2}{SPACE}")
            time.sleep(0.5)

            # --- 步骤 2: 设置 Confidence (Tab=6) ---
            # 你的测试：空白 -> Tab x6 -> Confidence
            # 相对计算：当前我们在 Agree (2)，还需要按 4 次 Tab 到达 Confidence (2+4=6)
            self.log("⚙️ Key-Nav: Setting Confidence to 0.82...")
            dlg.type_keys("{TAB 4}") 
            time.sleep(0.2)
            
            # 输入数值 (保险起见：全选 -> 删除 -> 输入)
            dlg.type_keys(f"^a{{DELETE}}{confidence}")
            time.sleep(0.5)

            # --- 步骤 3: 点击开始 (Tab=9) ---
            # 你的测试：空白 -> Tab x9 -> Start
            # 相对计算：当前我们在 Confidence (6)，还需要按 3 次 Tab 到达 Start (6+3=9)
            self.log("🚀 Key-Nav: Triggering Start...")
            dlg.type_keys("{TAB 3}")
            time.sleep(0.5)
            
            # 按回车键 (Enter) 触发按钮
            dlg.type_keys("{ENTER}")
            
            self.log("✅ Automation sequence finished via Keyboard.")
        except Exception as e:
            self.log(f"⚠️ GUI Automation failed: {e}")
            self.log("👉 Please manually set Confidence to 0.82 and Click Start.")

    def _monitor_results(self, total_expected, threshold, process):
        import pandas as pd 
        processed_files = set()
        
        # 增加超时机制，防止死循环
        no_file_count = 0 
        
        while len(processed_files) < total_expected:
            # 检查进程是否存活
            if process.poll() is not None and len(processed_files) < total_expected:
                self.log("⚠️ Engine closed unexpectedly.")
                break
            
            if os.path.exists(self.output_dir):
                files = [f for f in os.listdir(self.output_dir) if f.endswith(".xlsx") and "summaryall" not in f]
                
                new_files_found = False
                for f in files:
                    if f not in processed_files:
                        new_files_found = True
                        full_path = os.path.join(self.output_dir, f)
                        
                        # 调用计算层
                        success = False
                        result = {}
                        for _ in range(5): # 重试5次
                            result = StatsCalculator.process_excel(full_path, threshold)
                            if result['success']:
                                success = True
                                break
                            time.sleep(1)
                        
                        if success:
                            self._append_to_summary(result)
                            self.log(f"📊 {f}: Count={result['count']}, AvgSqrt={result['avg_sqrt_area']:.2f}")
                        else:
                            self.log(f"❌ Parse Error {f}: {result.get('error')}")

                        processed_files.add(f)
                
                # 如果这一轮没找到新文件，增加计数器，避免日志刷屏
                if not new_files_found:
                    no_file_count += 1
                else:
                    no_file_count = 0
                    
            time.sleep(2)
        
        self.log(f"🎉 All tasks finished. Report generated: {self.final_report}")

    def _append_to_summary(self, result_dict):
        import pandas as pd
        df = pd.DataFrame([{
            'File': result_dict['filename'],
            'Adjusted_Count': result_dict['count'], # 改名体现这是修正后的计数
            'Adjusted_Avg_Sqrt_Area': result_dict['avg_sqrt_area']
        }])
        header = not os.path.exists(self.final_report)
        df.to_csv(self.final_report, mode='a', index=False, header=header)