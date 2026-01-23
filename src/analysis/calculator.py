import pandas as pd
import numpy as np
import os

class StatsCalculator:
    @staticmethod
    def process_excel(file_path, threshold=0.0):
        """
        处理单个 Excel 文件，返回统计结果字典。
        """
        try:
            # 使用 openpyxl 引擎读取 xlsx
            df = pd.read_excel(file_path, engine='openpyxl')
            
            # 智能查找列名
            target_col = None
            for col in df.columns:
                c_lower = str(col).lower()
                if "area" in c_lower and "pixel" in c_lower:
                    target_col = col
                    break
                elif c_lower == "area":
                    target_col = col
                    break
            
            if not target_col:
                return {"success": False, "error": "Column 'Area' not found"}

            # 核心计算
            df['sqrt_area'] = np.sqrt(df[target_col])
            filtered = df[df['sqrt_area'] >= threshold]
            
            count = len(filtered)
            avg = filtered['sqrt_area'].mean() if count > 0 else 0.0

            return {
                "success": True,
                "filename": os.path.basename(file_path),
                "count": count,
                "avg_sqrt_area": avg
            }

        except Exception as e:
            return {"success": False, "error": str(e)}