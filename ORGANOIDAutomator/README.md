# ORGANOID Automator (类器官自动分析工具)

![Platform](https://img.shields.io/badge/platform-Windows-blue) ![Python](https://img.shields.io/badge/python-3.9+-green) ![License](https://img.shields.io/badge/license-MIT-orange)

[English Version Below](#organoid-automator-english)

**ORGANOID Automator** 是一个用于高通量类器官形态分析的自动化流水线工具。
它作为 **GelNestOrganoidV3** 的自动化包装器（Wrapper），通过 GUI 自动化技术实现了批量图像处理、无人值守运行以及数据自动汇总功能，将繁琐的人工操作减少 95% 以上。

---

## 🇨🇳 中文说明

### 🛠️ 核心功能
* **全自动批处理**：只需指定一个文件夹，即可处理数百张图片。
* **数据自动汇总**：自动收集生成的 Excel 结果，汇总并计算平均值（Avg Sqrt Area），生成最终的 `Final_Report.csv`。
* **智能监控**：实时监控文件生成，支持断点续传。
* **开箱即用**：绿色软件，无需安装 Python 环境。

### 📂 目录结构 (非常重要！)
为了让程序正常运行，请确保你的文件夹结构如下所示：

```text
你的文件夹/
├── ORGANOIDAutomator.exe        <-- 本程序 (启动入口)
├── README.md                    <-- 说明文档
└── GelNestOrganoidV3/           <-- [关键] 你必须手动创建这个文件夹并放入引擎
    ├── GelNestOrganoidV3.0.exe  <-- 引擎本体 (请确保名字完全一致)
    ├── img/                     <-- (程序会自动创建，请勿占用)
    └── outputs/                 <-- (程序会自动创建，结果会出现在这里)

```

### 🚀 快速开始 (3步走)

#### 第一步：部署引擎

1. 下载本程序 `ORGANOIDAutomator.exe`。
2. 下载 **GelNestOrganoidV3.0** 软件包（从其官方渠道）。
3. 解压 GelNest 包，将其中的所有文件放入本程序同级目录下的 `GelNestOrganoidV3` 文件夹中。
* *检查点：你应该能找到 `GelNestOrganoidV3/GelNestOrganoidV3.0.exe` 这个文件。*



#### 第二步：准备图片

准备一个文件夹（例如 `D:\MyExperiments\Batch1`），里面装满你需要处理的原始图片（支持 .jpg, .png, .tif 等常见格式）。

#### 第三步：启动分析

1. 双击运行 **`ORGANOIDAutomator.exe`**。
2. 点击 **Browse** 按钮，选择你在第二步准备的**图片文件夹**。
3. (可选) 在 Threshold 输入框设置阈值（最小 Sqrt Area），用于过滤杂质。
4. 点击 **🚀 INITIALIZE PIPELINE**。
5. **请勿触碰鼠标**：程序会自动打开 GelNest 窗口，自动点击“Start Processing”。
6. 等待进度条走完。最终汇总结果将保存在程序根目录下的 `BioQuant_Final_Report.csv` 中。

---

<a name="organoid-automator-english"></a>

# ORGANOID Automator (English)

**ORGANOID Automator** is a high-throughput automated pipeline for organoid morphology analysis.
Acting as a wrapper for the **GelNestOrganoidV3** engine, it utilizes GUI automation to enable batch processing, unattended execution, and automatic data aggregation, reducing manual workload by over 95%.

### 🛠️ Key Features

* **Batch Processing**: Process hundreds of images from a single directory automatically.
* **Data Aggregation**: Automatically parses generated Excel files, calculates metrics (Avg Sqrt Area), and compiles a master `Final_Report.csv`.
* **Smart Monitoring**: Real-time file system watchdog.
* **Portable**: No Python installation required. Drop and run.

### 📂 Directory Structure (Critical!)

For the software to function correctly, your directory must look exactly like this:

```text
Your_Folder/
├── ORGANOIDAutomator.exe        <-- This Tool (Run this)
├── README.md                    <-- Documentation
└── GelNestOrganoidV3/           <-- [CRITICAL] You must place the engine here
    ├── GelNestOrganoidV3.0.exe  <-- The Engine (Name must match exactly)
    ├── img/                     <-- (Created automatically)
    └── outputs/                 <-- (Created automatically)

```

### 🚀 Quick Start Guide

#### Step 1: Deploy the Engine

1. Download `ORGANOIDAutomator.exe`.
2. Download the **GelNestOrganoidV3.0** package (from the original provider).
3. Extract the contents of GelNest into the `GelNestOrganoidV3` folder (next to this executable).
* *Check: Ensure `GelNestOrganoidV3/GelNestOrganoidV3.0.exe` exists.*



#### Step 2: Prepare Images

Prepare a source folder (e.g., `D:\MyExperiments\Batch1`) containing all the raw images you want to analyze.

#### Step 3: Run Analysis

1. Double-click **`ORGANOIDAutomator.exe`**.
2. Click **Browse** and select your **Source Image Folder**.
3. (Optional) Set a **Threshold** (Min Sqrt Area) to filter noise.
4. Click **🚀 INITIALIZE PIPELINE**.
5. **Hands off**: The tool will automatically launch GelNest, click 'Start', and manage the workflow.
6. Wait for completion. The final aggregated report will be saved as `BioQuant_Final_Report.csv` in the root directory.

---

### ⚠️ Disclaimer (免责声明)

This software is an open-source automation wrapper designed to facilitate research efficiency.

* The core image analysis algorithm is powered by **GelNestOrganoidV3**, which is an external tool subject to its own license terms.
* We are not affiliated with the developers of GelNest.
* Please ensure you comply with the license usage of the GelNest engine.

```

```