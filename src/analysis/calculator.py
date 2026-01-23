import pandas as pd
import numpy as np
import os

class StatsCalculator:
    @staticmethod
    def process_excel(file_path, threshold=0.0):
        """
        处理单个 Excel 文件，应用几何修正算法：
        Real_Area ≈ Local_Area (BoundingBox) * Circularity
        
        【更新】：计算完成后，会将修正后的数据列写回原 Excel 文件，保证数据可追溯。
        """
        try:
            # 1. 读取 Excel
            # 使用 openpyxl 引擎
            df = pd.read_excel(file_path, engine='openpyxl')
            
            # 2. 智能查找关键列 (Area 和 Circularity)
            area_col = None
            circ_col = None
            
            for col in df.columns:
                c_str = str(col).lower().strip()
                # 找 Area
                if "area" in c_str and not area_col:
                    area_col = col
                # 找 Circularity
                if "circ" in c_str and not circ_col:
                    circ_col = col

            # 3. 校验列是否存在
            if not area_col:
                return {"success": False, "error": "Column 'Area' not found"}
            if not circ_col:
                return {"success": False, "error": "Column 'Circularity' not found"}

            # 4. 核心计算：几何修正
            # 新增列：Adjusted_Real_Area (修正后的真实面积)
            df['Adjusted_Real_Area'] = df[area_col] * df[circ_col]
            
            # 新增列：Sqrt_Real_Area (用于筛选的开根号值)
            df['Sqrt_Real_Area'] = np.sqrt(df['Adjusted_Real_Area'])
            
            # 5. 【关键修改】将计算结果写回 Excel
            # index=False 防止产生额外的索引列
            # 这样用户打开单个 Excel 也能看到我们算出来的结果
            try:
                df.to_excel(file_path, index=False, engine='openpyxl')
            except PermissionError:
                return {"success": False, "error": "File is open in Excel. Please close it."}
            except Exception as e:
                # 写回失败不应阻断流程，但记录警告
                print(f"Warning: Could not save back to {file_path}: {e}")

            # 6. 筛选 (根据用户设定的阈值，基于 Sqrt_Real_Area)
            filtered = df[df['Sqrt_Real_Area'] >= threshold]
            
            # 7. 统计输出
            count = len(filtered)
            avg = filtered['Sqrt_Real_Area'].mean() if count > 0 else 0.0

            return {
                "success": True,
                "filename": os.path.basename(file_path),
                "count": count,
                "avg_sqrt_area": avg
            }

        except Exception as e:
            return {"success": False, "error": str(e)}