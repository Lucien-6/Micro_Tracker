<div align="center">

```
 ███╗   ███╗██╗ ██████╗██████╗  ██████╗     ████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗
 ████╗ ████║██║██╔════╝██╔══██╗██╔═══██╗    ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
 ██╔████╔██║██║██║     ██████╔╝██║   ██║       ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
 ██║╚██╔╝██║██║██║     ██╔══██╗██║   ██║       ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
 ██║ ╚═╝ ██║██║╚██████╗██║  ██║╚██████╔╝       ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
 ╚═╝     ╚═╝╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝        ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
```

<h3><em>基于SAM2的显微视频目标分割和追踪工具</em></h3>
<h4>SAM2-based Microscopy Video Object Segmentation and Tracking Tool</h4>

</div>

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.2.0-brightgreen.svg" alt="Version 2.2.0">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0">
  <img src="https://img.shields.io/badge/PyQt5-5.15%2B-green.svg" alt="PyQt5 5.15+">
  <img src="https://img.shields.io/badge/SAM2-Supported-orange.svg" alt="SAM2 Supported">
  <img src="https://img.shields.io/badge/CUDA-11.7%2B-green?logo=nvidia" alt="CUDA 11.7+">
</p>

<div align="center">
  <a href="#english-version">English</a> | <a href="#chinese-version">中文</a>
</div>

---

<a id="english-version"></a>

# 🔬 Micro_Tracker [English]

Micro_Tracker is a powerful microscopy video analysis tool based on the SAM2 model, designed specifically for tracking and analyzing microscopic organisms and particles. The application provides an intuitive user interface with multi-frame annotation support, real-time mask preview, and advanced filtering capabilities, allowing researchers to easily mark, track, and analyze objects in microscopy videos with high precision.

## 🖥️ Application Interface

<div align="center">
  <table>
    <tr>
      <td align="center" width="33%">
        <img src="assets/screenshots/annotation_tab.png" alt="Annotation Tab" width="280"/><br/>
        <strong>🎯 Video Annotation</strong><br/>
        <em>Interactive object marking and tracking setup</em>
      </td>
      <td align="center" width="33%">
        <img src="assets/screenshots/result_tab.png" alt="Result Preview" width="280"/><br/>
        <strong>📊 Result Preview</strong><br/>
        <em>Preview the tracking result video</em>
      </td>
      <td align="center" width="33%">
        <img src="assets/screenshots/filter_tab.png" alt="Filter Analysis" width="280"/><br/>
        <strong>🔍 Advanced Filtering</strong><br/>
        <em>Sophisticated data analysis and export</em>
      </td>
    </tr>
  </table>
</div>

> 💡 **Note**: Screenshots show the application running on Windows 11 with a sample microscopy video of microorganisms. The interface adapts to different screen sizes and operating systems.

## Table of Contents 📚

- [Features](#-features)
- [System Requirements](#-system-requirements)
- [Installation Guide](#-installation-guide)
  - [1. Clone Repository](#1-clone-repository)
  - [2. Create Virtual Environment (Recommended)](#2-create-virtual-environment-recommended)
  - [3. Install Dependencies](#3-install-dependencies)
  - [4. Install SAM2](#4-install-sam2)
  - [5. Download Model Weights](#5-download-model-weights)
- [Usage](#-usage)
  - [Launch Application](#launch-application)
  - [Main Functionality Workflow](#main-functionality-workflow)
    - [1. Video Tracking](#1-video-tracking-️)
    - [2. Mask Filtering](#2-mask-filtering-)
  - [Keyboard Shortcuts](#keyboard-shortcuts-️)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
  - [Common Issues](#common-issues-)
- [License](#-license)
- [Acknowledgements](#-acknowledgements)

## ✨ Features

- **🎯 Object Segmentation and Tracking**: Utilize SAM2 (Segment Anything Model 2) and SAMRUAI for high-precision object segmentation and tracking. Fully compliant with SAM2 official API best practices.
- **📂 Flexible Input Sources**: Support both video files and image sequences as input:
  - **Video files**: Common formats like MP4, AVI, MOV
  - **Image sequences**: JPEG, PNG, TIFF, BMP formats with intelligent filename sorting
  - Auto-conversion for SAM2 compatibility (non-JPEG images automatically converted)
- **🎯 Multi-Frame Annotation**: Support multi-frame intelligent annotation with two modes - new object mode and refine object mode. Add annotations at key frames (deformation, occlusion) to significantly improve tracking quality.
- **👁️ Real-Time Preview**: Automatically generate mask preview using SAM2 after adding annotations, helping verify annotation quality instantly.
- **🔧 SAM2 API Alignment**:
  - Mixed prompt handling (box + points) follows SAM2 official implementation with single API call
  - Refinement mode enforces point prompts only (UI auto-constraints per SAM2 best practices)
  - Ensures optimal refinement quality and temporal consistency
- **📋 Annotation Management**: Comprehensive annotation management panel with frame list, quick jump, delete, and import/export functionality (JSON format).
- **🎬 Video Analysis**: Process microscopy videos and generate output videos with markers and trajectories using segmented forward propagation strategy.
- **📊 Data Extraction**: Extract key parameters such as position, size, and shape of target objects.
- **🎭 Mask Export**: Save segmentation results as mask images for subsequent analysis.
- **🔎 Filtering Function**: Filter target objects based on criteria like size, position, and speed.
- **📈 Data Export**: Export trajectory and morphological data of filtered objects as Excel spreadsheets for subsequent analysis.

## 💻 System Requirements

- **Operating System**: Windows 10/11 or Linux
- **Python Version**: 3.10+
- **Hardware**: NVIDIA GPU (at least 4GB VRAM) and CUDA 11.7+ (recommended)
- **Key Dependencies**:
  - PyQt5 >= 5.15.0
  - OpenCV >= 4.6.0
  - NumPy >= 1.20.0
  - PyTorch >= 2.0.0
  - Torchvision >= 0.15.0
  - Pandas >= 1.4.0
  - See `requirements.txt` for complete list

## 🚀 Installation Guide

### 1. Clone Repository

```bash
git clone https://github.com/Lucien-6/Micro_Tracker.git
cd Micro_Tracker
```

### 2. Create Virtual Environment (Recommended)

```bash
# Using conda
conda create -n microtracker python=3.10
conda activate microtracker

# Or using venv
python -m venv microtracker_env
# Windows
microtracker_env\\Scripts\\activate
# Linux/Mac
source microtracker_env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

**Important Notes**:

- **PyTorch & CUDA**: Please download and install PyTorch and Torchvision corresponding to your device's actual CUDA version. Visit the [PyTorch official website](https://pytorch.org/) to select the appropriate version.
- **Minimum Versions**: Ensure PyTorch >= 2.0.0 and Torchvision >= 0.15.0 for SAM2 compatibility.
- **GPU Support**: For GPU acceleration, make sure to install the CUDA-enabled version of PyTorch.

### 4. Install SAM2

```bash
cd models/sam2
pip install -e .
pip install -e ".[notebooks]"
```

### 5. Download Model Weights

SAM2 model weights need to be downloaded separately:

1. Visit the [SAM2 official repository](https://github.com/facebookresearch/segment-anything) to download model files, or click the following links directly:

   - [sam2.1_hiera_tiny.pt](https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_tiny.pt)
   - [sam2.1_hiera_small.pt](https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_small.pt)
   - [sam2.1_hiera_base_plus.pt](https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_base_plus.pt)
   - [sam2.1_hiera_large.pt](https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt)

2. Place the downloaded model files (`.pt` or `.pth`) in the `models/sam2/checkpoints` directory.

## 🛠️ Usage

### Launch Application

```bash
python -m main
```

### Main Functionality Workflow

#### 1. Video Tracking 🎞️

1. **Select Input Source**:

   - **Video File**: Select "Video File" radio button, then click "Browse" to select a video file (MP4, AVI, MOV, etc.)
   - **Image Sequence**: Select "Image Sequence" radio button, then click "Browse" to select a folder containing image files
     - Supported formats: JPEG, PNG, TIFF, BMP
     - Images will be automatically sorted by filename (supports patterns like `001.jpg`, `frame_001.png`, etc.)
     - Non-JPEG images will be automatically converted for SAM2 compatibility
     - Default playback rate: 10 FPS (configurable)

2. Select the SAM2 model and set output directory.
3. **Multi-Frame Intelligent Annotation**:

   **New Object Annotation**:

   - Select "🆕 New Object" mode
   - Browse to the frame where the object first appears (usually frame 0)
   - Hold left mouse button and drag to draw bounding box
   - System automatically assigns unique ID and fixed color
   - Real-time preview mask will be automatically generated and displayed

   **Refine Object Annotation**:

   - Select "✏️ Refine Object" mode
   - Choose the object ID to refine from dropdown
   - Browse to key frames (deformation, occlusion, etc.)
   - **Use point clicks** to refine the object (click on target areas)
   - Note: Box drawing is disabled in refine mode per SAM2 best practices
   - The object being refined will be highlighted with golden dashed line

   **Best Practices**:

   - Annotate at frame 0 when object first appears
   - Add annotations when object shape changes significantly
   - Add annotations before and after occlusion
   - Recommend 5-10 key frames, not too many

   **Annotation Management**:

   - View all annotated frames in the annotation panel
   - Click "Jump" to quickly navigate to specific frames
   - Click "Delete" to remove unwanted annotations
   - Use "Export Annotations" to save annotation data as JSON file
   - Use "Import Annotations" to restore annotation data from JSON file

4. Click the "**Start Processing**" button.
5. System will automatically detect annotation mode and apply SAM2 prompts at each annotated frame using segmented forward propagation strategy to significantly improve tracking quality.
6. After processing is complete, preview the output video and view analysis results in the "**Result Preview**" tab.

#### 2. Mask Filtering 🎭

1. Go to the "**Filter**" tab.
2. Select the directory containing mask files.
3. Set filtering parameters (e.g., area range, instantaneous velocity, displacement, area change rate, etc.).
4. You can specify object IDs to exclude (separate multiple IDs with commas).
5. Click the "**Apply Filter**" button.
6. View filtering results and statistics, including details of objects that passed filtering, were partially truncated, or completely filtered.
7. Click "**Save Results**" to export filtered mask images and trajectory data (Excel format).

### Keyboard Shortcuts ⌨️

#### Video Control

| Shortcut | Function         |
| -------- | ---------------- |
| `Space`  | Play/Pause video |
| `F`      | Next frame       |
| `D`      | Previous frame   |

#### Annotation Editing

| Shortcut | Function                         |
| -------- | -------------------------------- |
| `Del`    | Delete selected bounding box     |
| `A`      | Save temporary clicks            |
| `Ctrl+C` | Clear temporary clicks           |
| `Ctrl+S` | Save clicks and go to next frame |

#### Mode Switching

| Shortcut | Function                            |
| -------- | ----------------------------------- |
| `Ctrl+Q` | Toggle prompt type (Box/Point mode) |
| `Ctrl+H` | Hide/Show prompt markers            |

#### Mouse Operations

| Action       | Function                            |
| ------------ | ----------------------------------- |
| Left drag    | Draw bounding box (New Object mode) |
| Left click   | Add positive point (Point mode)     |
| Right click  | Add negative point (Point mode)     |
| Click on box | Select bounding box                 |

## 📁 Project Structure

```
Micro_Tracker/
├── micro_tracker/           # Main application code
│   ├── components/          # UI components
│   ├── config/              # Configuration files
│   ├── controllers/         # MVC controllers
│   ├── threads/             # Processing threads
│   ├── ui/                  # UI interface
│   └── utils/               # Utility functions
├── models/                  # Models directory
│   └── sam2/                # SAM2 model
│       ├── checkpoints/     # Model weight files directory
│       ├── sam2/            # SAM2 source code
│       └── ...              # Other SAM2 related files
├── utils/                   # Utility scripts
├── scripts/                 # Processing scripts
├── assets/                  # Resource files
├── icons/                   # UI icons
├── main.py                  # Application entry script
├── requirements.txt         # Dependencies list
├── README.md                # Project description
└── LICENSE                  # Project license
```

## 🩺 Troubleshooting

### Common Issues ❓

1. **Startup Failure**

   - Check if the Python version is 3.10+.
   - Ensure all dependencies are correctly installed (refer to [Install Dependencies](#3-install-dependencies)).

2. **GPU Memory Insufficient**

   - Try reducing the resolution of the processing video.
   - Reduce the number of targets being tracked simultaneously.

3. **Tracking Inaccurate**

   - Ensure the accuracy of initial framing.
   - Try using higher quality or clearer videos.

4. **Processing Speed Slow**
   - Confirm if the GPU is being used by the program (usually there will be relevant logs during program startup or processing).
   - Consider using a more powerful GPU.

## 📜 License

This project is licensed under the [Apache 2.0 License](LICENSE).

## 🙏 Acknowledgements

This project was created based on the following excellent projects and gained many inspirations from them:

- [SAMURAI](https://github.com/yangchris11/samurai)
- [SAM2 (Segment Anything Model 2)](https://github.com/facebookresearch/sam2)
- [Lang2SegTrack](https://github.com/wngkj/Lang2SegTrack)

---

<a id="chinese-version"></a>

# 🔬 Micro_Tracker [中文]

Micro_Tracker 是一个功能强大的基于 SAM2 模型的显微镜视频分析工具，专为微观生物体和颗粒的跟踪和分析而设计。该应用提供直观的用户界面，支持多帧智能标注、实时 mask 预览和高级筛选功能，使研究人员能够高精度地标记、跟踪和分析显微镜视频中的目标物体。

## 🖥️ GUI 界面

<div align="center">
  <table>
    <tr>
      <td align="center" width="33%">
        <img src="assets/screenshots/annotation_tab.png" alt="Annotation Tab" width="280"/><br/>
        <strong>🎯 视频标注</strong><br/>
        <em>交互式目标标记和追踪设置</em>
      </td>
      <td align="center" width="33%">
        <img src="assets/screenshots/result_tab.png" alt="Result Preview" width="280"/><br/>
        <strong>📊 结果预览</strong><br/>
        <em>预览追踪结果视频</em>
      </td>
      <td align="center" width="33%">
        <img src="assets/screenshots/filter_tab.png" alt="Filter Analysis" width="280"/><br/>
        <strong>🔍 高级筛选</strong><br/>
        <em>精密的数据分析和导出功能</em>
      </td>
    </tr>
  </table>
</div>

> 💡 **说明**: 截图展示了应用程序在 Windows 11 系统上运行微生物显微视频样本的界面。界面可适应不同屏幕尺寸和操作系统。

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
- [项目结构](#-项目结构)
- [故障排除](#-故障排除)
  - [常见问题-](#常见问题-)
- [许可证](#-许可证)
- [致谢](#-致谢)

## ✨ 功能特点

- **🎯 目标分割跟踪**：利用 SAM2（Segment Anything Model 2）和 SAMRUAI 实现高精度的目标分割和跟踪。完全符合 SAM2 官方 API 最佳实践。
- **📂 灵活的输入源**：同时支持视频文件和图像序列作为输入：
  - **视频文件**：支持 MP4、AVI、MOV 等常见格式
  - **图像序列**：支持 JPEG、PNG、TIFF、BMP 格式，智能文件名排序
  - 自动格式转换以兼容 SAM2（非 JPEG 图像自动转换）
- **🎯 多帧智能标注**：支持在视频任意帧添加标注，提供"新对象"和"修正对象"两种模式。在关键帧（形变、遮挡）添加标注可显著提升追踪质量。
- **👁️ 实时预览功能**：添加标注后自动使用 SAM2 生成 mask 预览，实时验证标注质量。
- **🔧 SAM2 API 对齐**：
  - 混合提示处理（box + points）遵循 SAM2 官方实现方式，单次 API 调用
  - 修正模式强制使用点击提示（UI 自动约束符合 SAM2 最佳实践）
  - 确保最优的 refinement 质量和时序一致性
- **📋 标注管理功能**：完善的标注管理面板，支持帧列表查看、快速跳转、删除和导入/导出（JSON 格式）。
- **🎬 视频分析**：处理显微镜视频并生成带有标记和轨迹的输出视频，采用分段前向传播策略。
- **📊 数据提取**：提取目标物体的位置、大小、形状等关键参数。
- **🎭 掩膜导出**：将分割结果保存为掩膜图像，便于后续分析。
- **🔎 筛选功能**：根据尺寸、位置、速度等条件筛选目标物体。
- **📈 数据导出**：将通过筛选的对象轨迹与形态数据输出保存为 Excel 表格，便于后续分析使用。

## 💻 系统要求

- **操作系统**：Windows 10/11 或 Linux
- **Python 版本**：3.10+
- **硬件**：NVIDIA GPU (至少 4GB 显存) 和 CUDA 11.7+ (推荐)
- **核心依赖**：
  - PyQt5 >= 5.15.0
  - OpenCV >= 4.6.0
  - NumPy >= 1.20.0
  - PyTorch >= 2.0.0
  - Torchvision >= 0.15.0
  - Pandas >= 1.4.0
  - 完整列表请参见 `requirements.txt`

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

**重要说明**：

- **PyTorch 与 CUDA**：请根据您设备实际的 CUDA 版本下载并安装相应的 PyTorch 和 Torchvision。访问 [PyTorch 官网](https://pytorch.org/) 选择合适的版本。
- **最低版本要求**：确保 PyTorch >= 2.0.0 和 Torchvision >= 0.15.0 以保证 SAM2 兼容性。
- **GPU 支持**：如需 GPU 加速，请确保安装支持 CUDA 的 PyTorch 版本。

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
python -m main
```

### 主要功能使用流程

#### 1. 视频跟踪 🎞️

1.  **选择输入源**：

    - **视频文件**：选择"视频文件"单选按钮，点击"浏览"选择视频文件（MP4、AVI、MOV 等）
    - **图像序列**：选择"图像序列"单选按钮，点击"浏览"选择包含图像文件的文件夹
      - 支持格式：JPEG、PNG、TIFF、BMP
      - 图像会按文件名自动排序（支持 `001.jpg`、`frame_001.png` 等命名格式）
      - 非 JPEG 图像会自动转换以兼容 SAM2
      - 默认播放帧率：10 FPS（可配置）

2.  选择 SAM2 模型并设置输出目录。
3.  **多帧智能标注**（推荐使用以获得最佳追踪效果）:

    **新对象标注**:

    - 选择"🆕 新对象"模式
    - 浏览到对象首次出现的帧（通常是第 0 帧）
    - 按住鼠标左键拖动绘制边界框
    - 系统自动分配唯一 ID 和固定颜色
    - 实时预览 mask 会自动生成并显示

    **修正对象标注**:

    - 选择"✏️ 修正对象"模式
    - 从下拉框选择要修正的对象 ID
    - 浏览到关键帧（对象形变、遮挡前后等）
    - **使用点击提示**精细化修正对象（点击目标区域）
    - 注意：修正模式下禁用边界框绘制（符合 SAM2 最佳实践）
    - 正在修正的对象会以金色虚线高亮显示

    **标注最佳实践**:

    - 在第 0 帧标注对象首次出现位置
    - 在对象形状显著变化时添加标注
    - 在对象被遮挡前后添加标注
    - 建议标注 5-10 个关键帧，不宜过多

    **标注管理**:

    - 在"标注管理"面板查看所有已标注帧
    - 点击"跳转"快速定位到指定标注帧
    - 点击"删除"移除不需要的标注
    - 使用"导出标注"保存标注数据为 JSON 文件
    - 使用"导入标注"从 JSON 文件恢复标注数据

4.  点击 "**开始处理**" 按钮。
5.  系统会自动检测标注模式，在每个标注帧应用 SAM2 提示，采用分段前向传播策略，显著提升追踪质量。
6.  处理完成后，在 "**结果预览**" 标签页查看结果。

#### 2. 掩膜筛选 🎭

1.  进入 "**筛选过滤**" 标签页。
2.  选择包含掩膜文件的目录。
3.  设置筛选参数 (例如：面积范围、瞬时速度、位移、面积变化率等)。
4.  可以指定要排除的对象 ID（多个 ID 用逗号分隔）。
5.  点击 "**应用筛选**" 按钮。
6.  查看筛选结果和统计信息，包括通过筛选、部分截断和完全过滤的对象详情。
7.  点击 "**保存结果**" 导出筛选后的掩膜图像和轨迹数据（Excel 格式）。

### 快捷键 ⌨️

#### 视频控制

| 快捷键 | 功能          |
| ------ | ------------- |
| `空格` | 播放/暂停视频 |
| `F`    | 下一帧        |
| `D`    | 上一帧        |

#### 标注编辑

| 快捷键   | 功能                       |
| -------- | -------------------------- |
| `Del`    | 删除当前选中的边界框       |
| `A`      | 保存临时点击               |
| `Ctrl+C` | 清除临时点击               |
| `Ctrl+S` | 保存临时点击并切换到下一帧 |

#### 模式切换

| 快捷键   | 功能                            |
| -------- | ------------------------------- |
| `Ctrl+Q` | 切换提示类型（边界框/点击模式） |
| `Ctrl+H` | 隐藏/显示提示标记               |

#### 鼠标操作

| 操作       | 功能                     |
| ---------- | ------------------------ |
| 左键拖拽   | 绘制边界框（新对象模式） |
| 左键点击   | 添加正向点击（点击模式） |
| 右键点击   | 添加负向点击（点击模式） |
| 单击边界框 | 选中边界框               |

## 📁 项目结构

```
Micro_Tracker/
├── micro_tracker/           # 主要应用代码
│   ├── components/          # UI组件
│   ├── config/              # 配置文件
│   ├── controllers/         # MVC控制器
│   ├── threads/             # 处理线程
│   ├── ui/                  # UI界面
│   └── utils/               # 工具函数
├── models/                  # 模型目录
│   └── sam2/                # SAM2模型
│       ├── checkpoints/     # 模型权重文件目录
│       ├── sam2/            # SAM2源代码
│       └── ...              # 其他SAM2相关文件
├── utils/                   # 工具脚本
├── scripts/                 # 处理脚本
├── assets/                  # 资源文件
├── icons/                   # UI图标
├── main.py                  # 应用入口脚本
├── requirements.txt         # 依赖列表
├── README.md                # 项目说明
└── LICENSE                  # 项目许可证
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

<p align="center"><em>Keep moving, keep thinking!</em></p>
