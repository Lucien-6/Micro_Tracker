[//]: <> (The following is a suggested table of contents. You can adjust it as needed.)

<!-- Badges -->
<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0">
  <!-- Add more badges here if needed, e.g., build status, version, etc. -->
</p>

# 🔬 Micro_Tracker

Micro_Tracker 是一个基于 SAM2 模型的显微镜图像/视频分析工具，专为微观生物体和颗粒的跟踪和分析而设计。该应用提供直观的用户界面，使研究人员能够轻松地标记、跟踪和分析显微镜下的目标物体。

## 目录 📚

- [功能特点](#-功能特点)
- [系统要求](#-系统要求)
- [安装指南](#-安装指南)
  - [1-克隆仓库](#1-克隆仓库)
  - [2-创建虚拟环境-推荐](#2-创建虚拟环境-推荐)
  - [3-安装依赖](#3-安装依赖)
  - [4-安装-sam2](#4-安装-sam2)
  - [5-下载模型权重文件](#5-下载模型权重文件)
- [使用方法](#-使用方法)
  - [启动应用](#启动应用)
  - [主要功能使用流程](#主要功能使用流程)
    - [1-视频跟踪-️](#1-视频跟踪-️)
    - [2-掩膜筛选-](#2-掩膜筛选-)
  - [快捷键-️](#快捷键-️)
- [文件结构](#-文件结构)
- [故障排除](#-故障排除)
  - [常见问题-](#常见问题-)
- [许可证](#-许可证)
- [致谢](#-致谢)

## ✨ 功能特点

- **🎯 实时目标跟踪**：利用 SAM2（Segment Anything Model 2）和 SAMRUAI 实现高精度的目标分割和跟踪。
- **✍️ 手动标注**：支持手动框选感兴趣区域 (ROI)。
- **🎬 视频分析**：处理显微镜视频并生成带有标记和轨迹的输出视频。
- **📊 数据提取**：提取目标物体的位置、大小、形状等关键参数。
- **🎭 掩膜导出**：将分割结果保存为掩膜图像，便于后续分析。
- **🔎 筛选功能**：根据尺寸、位置、速度等条件筛选目标物体。
- **📈 数据导出**：将通过筛选的对象轨迹与形态数据输出保存为 Excel 表格，便于后续分析使用。

## 💻 系统要求

- 操作系统：Windows 11 或 Linux
- Python 版本：3.10+
- 硬件：NVIDIA GPU (至少 4GB 显存) 和 CUDA 11.7+ (推荐)

## 🚀 安装指南

### 1. 克隆仓库

```bash
git clone https://github.com/Lucien-6/Micro_Tracker.git
cd Micro_Tracker
```

### 2. 创建虚拟环境 (推荐)

```bash
# 使用 conda
conda create -n microtracker python=3.10
conda activate microtracker

# 或使用 venv
python -m venv microtracker_env
# Windows
microtracker_env\\Scripts\\activate
# Linux/Mac
source microtracker_env/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

**注意**：请根据您设备实际的 CUDA 版本下载并安装相应的 PyTorch 和 Torchvision。您可以访问 [PyTorch 官网](https://pytorch.org/) 获取更多信息。

### 4. 安装 SAM2

```bash
cd models/sam2
pip install -e .
pip install -e ".[notebooks]"
```

### 5. 下载模型权重文件

SAM2 模型权重文件需要单独下载：

1.  访问 [SAM2 官方仓库](https://github.com/facebookresearch/segment-anything) 下载模型文件，或直接点击以下链接下载：

    - [sam2.1_hiera_tiny.pt](https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_tiny.pt)
    - [sam2.1_hiera_small.pt](https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_small.pt)
    - [sam2.1_hiera_base_plus.pt](https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_base_plus.pt)
    - [sam2.1_hiera_large.pt](https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt)

2.  将下载的模型文件 (`.pt` 或 `.pth`) 放置在 `models/sam2/checkpoints` 目录下。

## 🛠️ 使用方法

### 启动应用

```bash
python -m micro_tracker.py
```

### 主要功能使用流程

#### 1. 视频跟踪 🎞️

1.  点击 "**浏览**" 按钮选择显微镜视频文件和 SAM2 模型。
2.  设置输出目录和相关参数。
3.  在视频的第一帧上框选要跟踪的目标 (可以框选多个目标)。
4.  点击 "**开始处理**" 按钮。
5.  处理完成后，可以在 "**结果预览**" 标签页预览输出视频和查看分析结果。

#### 2. 掩膜筛选 🎭

1.  进入 "**筛选过滤**" 标签页。
2.  选择包含掩膜文件的目录。
3.  设置筛选参数 (例如：面积范围、瞬时速率等)。
4.  点击 "**应用筛选**" 按钮。
5.  查看筛选结果和统计信息。
6.  点击 "**输出保存**" 导出筛选后的数据。

### 快捷键 ⌨️

- **空格键**: 播放/暂停视频
- **D**: 下一帧
- **F**: 上一帧
- **Del**: 删除当前选中的框

## 📁 文件结构

```
Micro_Tracker/
├── SAM_tracker.py         # Main application script
├── requirements.txt       # List of dependencies
├── README.md              # Project description
├── LICENSE                # Project license
├── models/                # Models directory
│   └── sam2/              # SAM2 model
│       ├── checkpoints/   # Directory for model weights
│       └── ...            # Other SAM2 related files
├── utils/                 # Utility functions
├── scripts/               # Processing scripts
├── assets/                # Asset files (e.g., images, icons if not in a separate folder)
└── icons/                 # UI icons
```

## 🩺 故障排除

### 常见问题 ❓

1.  **启动失败**

    - 检查 Python 版本是否为 3.10+。
    - 确保所有依赖项已正确安装 (参照 [安装依赖](#3-安装依赖))。

2.  **GPU 内存不足**

    - 尝试降低处理视频的分辨率。
    - 减少同时跟踪的目标数量。

3.  **跟踪不准确**

    - 确保初始框选的准确性。
    - 尝试使用更高质量或更清晰的视频。

4.  **处理速度慢**
    - 确认 GPU 是否正在被程序使用 (通常在程序启动时或处理过程中会有相关日志)。
    - 考虑使用性能更强的 GPU。

## 📜 许可证

本项目采用 [Apache 2.0 许可证](LICENSE)。

## 🙏 致谢

本项目基于以下优秀项目创建，并从中获得了诸多启发：

- [SAMURAI](https://github.com/yangchris11/samurai)
- [SAM2 (Segment Anything Model 2)](https://github.com/facebookresearch/sam2)
- [Lang2SegTrack](https://github.com/wngkj/Lang2SegTrack)

---

<p align="center"><em>Keep moving, keep thinking！</em></p>
