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
        self.final_report = os.path.join(self.project_root, "BioQuant_Final_Report.csv")

    def run(self, source_folder, threshold):
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
            self._automate_gui()

            # 5. 监控与计算
            self._monitor_results(len(images), threshold, process)

        except Exception as e:
            self.log(f"❌ Critical Error: {str(e)}")

    def _prepare_directories(self):
        if os.path.exists(self.img_dir): shutil.rmtree(self.img_dir)
        if os.path.exists(self.output_dir): shutil.rmtree(self.output_dir)
        os.makedirs(self.img_dir)
        os.makedirs(self.output_dir)

    def _automate_gui(self):
        self.log("🤖 Waiting for GUI...")
        try:
            app = Application(backend="uia").connect(path=self.exe_path, timeout=20)
            dlg = app.window(title_re=".*GelNestOrganoid.*")
            dlg.wait('visible', timeout=30)
            dlg.set_focus()
            time.sleep(1)
            
            rect = dlg.rectangle()
            w, h = rect.width(), rect.height()

            # 盲点坐标 (根据之前的经验)
            self.log("👆 Auto-clicking: Disclaimer...")
            dlg.click_input(coords=(int(w * 0.35), int(h * 0.22)))
            time.sleep(0.5)
            
            self.log("👆 Auto-clicking: Start Processing...")
            dlg.click_input(coords=(int(w * 0.5), int(h * 0.82)))
            self.log("✅ Automation sequence finished. Watching for data...")
        except Exception as e:
            self.log(f"⚠️ GUI Automation failed: {e}")
            self.log("👉 Please manually click 'Start' in the external window.")

    def _monitor_results(self, total_expected, threshold, process):
        import pandas as pd 
        processed_files = set()
        
        while len(processed_files) < total_expected:
            if process.poll() is not None and len(processed_files) < total_expected:
                self.log("⚠️ Process terminated early.")
                break
            
            if os.path.exists(self.output_dir):
                files = [f for f in os.listdir(self.output_dir) if f.endswith(".xlsx") and "summaryall" not in f]
                
                for f in files:
                    if f not in processed_files:
                        # 发现新文件 -> 调用 Calculation 模块
                        full_path = os.path.join(self.output_dir, f)
                        
                        # 重试读取机制
                        success = False
                        result = {}
                        for _ in range(5):
                            try:
                                result = StatsCalculator.process_excel(full_path, threshold)
                                if result['success']:
                                    success = True
                                    break
                            except:
                                time.sleep(1)
                        
                        if success:
                            # 写入总表
                            self._append_to_summary(result)
                            self.log(f"📊 Processed: {f} -> Avg: {result['avg_sqrt_area']:.2f}")
                        else:
                            self.log(f"❌ Failed to parse {f}: {result.get('error')}")

                        processed_files.add(f)
            time.sleep(2)
        
        self.log(f"🎉 Pipeline Complete. Report: {self.final_report}")

    def _append_to_summary(self, result_dict):
        import pandas as pd
        df = pd.DataFrame([{
            'File': result_dict['filename'],
            'Count': result_dict['count'],
            'Avg_Sqrt_Area': result_dict['avg_sqrt_area']
        }])
        header = not os.path.exists(self.final_report)
        df.to_csv(self.final_report, mode='a', index=False, header=header)