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
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-Apache_2.0-blue.svg" alt="License: Apache 2.0">
  <img src="https://img.shields.io/badge/PyQt5-5.15%2B-green.svg" alt="PyQt5 5.15+">
  <img src="https://img.shields.io/badge/SAM2-Supported-orange.svg" alt="SAM2 Supported">
  <img src="https://img.shields.io/badge/CUDA-11.7%2B-green?logo=nvidia" alt="CUDA 11.7+">
  <!-- More badges as needed -->
</p>

<div align="center">
  <a href="#english-version">English</a> | <a href="#chinese-version">中文</a>
</div>

---

<a id="english-version"></a>

# 🔬 Micro_Tracker [English]

Micro_Tracker is a microscopy image/video analysis tool based on the SAM2 model, designed specifically for tracking and analyzing microscopic organisms and particles. The application provides an intuitive user interface that allows researchers to easily mark, track, and analyze objects under a microscope.

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

### Core Segmentation & Tracking
- **🎯 Object Segmentation and Tracking**: Utilize SAM2 (Segment Anything Model 2) for high-precision object segmentation and tracking.
- **🔄 Multi-Frame Annotation**: Add annotations on any frame in the video, with intelligent object ID management and color consistency.
- **✨ Real-Time Mask Preview**: Automatically displays predicted masks while annotating, providing instant visual feedback.
- **✏️ Click-Based Refinement**: Add positive/negative points (A key) to refine masks on keyframes with shape changes or occlusions.

### Data Management & Analysis
- **📊 Data Extraction**: Extract key parameters such as position, size, and shape of target objects.
- **🎭 Mask Export**: Save segmentation results as mask images for subsequent analysis.
- **🔎 Advanced Filtering**: Filter target objects based on criteria like area, velocity, displacement, and area change rate.
- **📈 Data Export**: Export trajectory and morphological data as Excel spreadsheets for subsequent analysis.

### User Interface
- **📝 Annotation Management**: View, jump to, delete annotations with an intuitive management panel.
- **💾 Import/Export**: Save and load annotations in JSON format for session persistence.
- **🎬 Video Playback**: Built-in video player with frame-by-frame navigation and playback controls.

## 💻 System Requirements

- Operating System: Windows 10/11 or Linux
- Python Version: 3.10+
- Hardware: NVIDIA GPU (at least 4GB VRAM) and CUDA 11.7+ (recommended)

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

**Note**: Please download and install PyTorch and Torchvision corresponding to your device's actual CUDA version. You can visit the [PyTorch official website](https://pytorch.org/) for more information.

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

**Initial Setup:**
1. Click the "**Browse**" button to select microscopy video files and the SAM2 model.
2. Set output directory and related parameters.
3. The real-time mask preview feature will automatically initialize when the video loads.

**Multi-Frame Intelligent Annotation:**

**Adding New Objects:**
- Select "🆕 New Object" mode
- Navigate to any frame and draw a bounding box around the object
- System automatically assigns a unique ID and consistent color
- **Real-time preview**: Predicted mask appears instantly as you annotate

**Refining Existing Objects:**
- Select "✏️ Refine Object" mode
- Choose the target object from the dropdown menu
- Navigate to keyframes (e.g., shape changes, occlusions)
- Draw a new bounding box for the same object (maintains ID and color)
- **Click refinement**: Press **A** key to add positive points for mask correction
- The object will be highlighted with a golden dashed outline during refinement

**Annotation Management:**
- View all annotated frames in the "Annotation Management" panel
- Click "Jump" to quickly navigate to any annotated frame
- Click "Delete" to remove unwanted annotations
- Use "Export/Import" to save and load annotations in JSON format

**Processing:**
4. Click the "**Start Processing**" button.
5. The system applies SAM2 prompts at each annotated frame, significantly improving tracking quality.
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

**Video Navigation:**
- **Space Bar**: Play/Pause video
- **D**: Next frame
- **F**: Previous frame

**Annotation Operations:**
- **A**: Add positive point (for mask refinement in "Refine Object" mode)
- **Del**: Delete currently selected bounding box

> 💡 **Tip**: Use the **A** key to add positive points on keyframes where the object shape changes significantly. This helps SAM2 maintain accurate tracking through occlusions and deformations.

### Best Practices 📌

**When to Add Annotations:**
1. **Frame 0**: When the object first appears
2. **Deformation Frames**: When the object's shape changes significantly
3. **Before/After Occlusions**: Before the object is occluded and after it reappears

**Annotation Strategy:**
- Keep the number of annotated frames reasonable (recommended: 5-10 keyframes)
- Prioritize annotating frames where tracking fails
- Use "Refine Object" mode to maintain consistent object IDs
- Leverage the real-time preview to verify annotation quality instantly

**Performance Tips:**
- Use the **tiny** or **small** model for faster processing on lower-end GPUs
- Reduce video resolution if encountering memory issues
- Close unnecessary applications to free up GPU memory

## 📁 Project Structure

```
Micro_Tracker/
├── micro_tracker/                    # Main application code
│   ├── components/                   # UI components
│   │   ├── custom_widgets.py        # Custom PyQt5 widgets
│   │   └── video_widgets.py         # Video display and overlay
│   ├── config/                       # Configuration files
│   │   └── style.py                  # UI styling
│   ├── controllers/                  # MVC controllers
│   │   ├── filter_controller.py     # Filtering logic
│   │   └── processing_controller.py # Video processing control
│   ├── threads/                      # Processing threads
│   │   ├── processing_thread.py     # SAM2 video processing
│   │   ├── filter_*.py               # Filtering threads
│   │   └── video_thread.py           # Video playback
│   ├── ui/                           # UI interface
│   │   ├── main_window.py            # Main window
│   │   ├── setup_tab.py              # Annotation tab
│   │   ├── result_preview_tab.py    # Results tab
│   │   ├── filter_tab.py             # Filtering tab
│   │   ├── annotation_manager.py    # Annotation management
│   │   └── ...                       # Other UI modules
│   └── utils/                        # Utility functions
│       └── preview_manager.py        # Real-time mask preview
├── models/                           # Models directory
│   └── sam2/                         # SAM2 model
│       ├── checkpoints/              # Model weight files (.pt)
│       └── sam2/                     # SAM2 source code
├── utils/                            # Shared utility scripts
│   ├── color.py                      # Color utilities
│   └── utils.py                      # General utilities
├── scripts/                          # Processing scripts
│   └── process_video_multiframe.py  # Multi-frame processing core
├── assets/                           # Resource files
│   ├── screenshots/                  # UI screenshots
│   └── *.mp4                         # Demo videos
├── icons/                            # UI icons
├── main.py                           # Application entry point
├── requirements.txt                  # Python dependencies
├── CHANGELOG.md                      # Version history
├── README.md                         # This file
└── LICENSE                           # Apache 2.0 License
```

## 🩺 Troubleshooting

### Common Issues ❓

1. **Startup Failure**

   - Check if the Python version is 3.10+.
   - Ensure all dependencies are correctly installed (refer to [Install Dependencies](#3-install-dependencies)).
   - Verify SAM2 installation: `cd models/sam2 && pip install -e .`

2. **GPU Memory Insufficient**

   - Try reducing the resolution of the processing video.
   - Reduce the number of targets being tracked simultaneously.
   - Use a smaller model (tiny or small instead of large).
   - Close the real-time preview if needed (though it's lightweight).

3. **Real-Time Preview Not Showing**

   - Check the log messages for preview initialization status.
   - Verify the model path is correctly configured.
   - Ensure the video is loaded successfully.
   - Try reloading the video to re-initialize the preview.

4. **Tracking Inaccurate**

   - Ensure the accuracy of initial framing.
   - Add more keyframe annotations where tracking fails.
   - Use the **A** key to add positive points for refinement.
   - Try using higher quality or clearer videos.

5. **Processing Speed Slow**
   - Confirm if the GPU is being used by the program (check logs during startup or processing).
   - Consider using a more powerful GPU.
   - Reduce the number of annotated frames if possible.
   - Use a smaller SAM2 model variant.

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

Micro_Tracker 是一个基于 SAM2 模型的显微镜图像/视频分析工具，专为微观生物体和颗粒的跟踪和分析而设计。该应用提供直观的用户界面，使研究人员能够轻松地标记、跟踪和分析显微镜下的目标物体。

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

### 核心分割与追踪
- **🎯 目标分割跟踪**：利用 SAM2（Segment Anything Model 2）实现高精度的目标分割和跟踪。
- **🔄 多帧智能标注**：在视频的任意帧添加标注，支持智能对象ID管理和颜色一致性。
- **✨ 实时mask预览**：标注时自动显示预测的mask，提供即时视觉反馈。
- **✏️ 点击修正功能**：在关键帧（形变、遮挡）添加正向/负向点（A键）以修正mask。

### 数据管理与分析
- **📊 数据提取**：提取目标物体的位置、大小、形状等关键参数。
- **🎭 掩膜导出**：将分割结果保存为掩膜图像，便于后续分析。
- **🔎 高级筛选**：根据面积、速度、位移、面积变化率等条件筛选目标物体。
- **📈 数据导出**：将轨迹与形态数据导出为 Excel 表格，便于后续分析。

### 用户界面
- **📝 标注管理**：通过直观的管理面板查看、跳转、删除标注。
- **💾 导入/导出**：以JSON格式保存和加载标注，支持会话持久化。
- **🎬 视频播放**：内置视频播放器，支持逐帧导航和播放控制。

## 💻 系统要求

- 操作系统：Windows 10/11 或 Linux
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
python -m main
```

### 主要功能使用流程

#### 1. 视频跟踪 🎞️

**初始设置：**
1.  点击 "**浏览**" 按钮选择显微镜视频文件和 SAM2 模型。
2.  设置输出目录和相关参数。
3.  加载视频时，实时mask预览功能会自动初始化。

**多帧智能标注：**

**添加新对象：**
- 选择"🆕 新对象"模式
- 浏览到任意帧，绘制新对象的边界框
- 系统自动分配唯一ID和固定颜色
- **实时预览**：标注时立即显示预测的mask

**修正现有对象：**
- 选择"✏️ 修正对象"模式
- 从下拉框选择要修正的对象
- 浏览到关键帧（如对象形变、遮挡处）
- 绘制该对象的新边界框（保持相同ID和颜色）
- **点击修正**：按 **A** 键添加正向点以修正mask
- 修正时该对象会以金色虚线高亮显示

**标注管理：**
- 在"标注管理"面板查看所有标注帧
- 点击"跳转"快速定位到任意标注帧
- 点击"删除"移除不需要的标注
- 使用"导出/导入"以JSON格式保存和加载标注

**处理：**
4.  点击 "**开始处理**" 按钮。
5.  系统会在每个标注帧应用SAM2提示，显著提升追踪质量。
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

**视频导航：**
- **空格键**: 播放/暂停视频
- **D**: 下一帧
- **F**: 上一帧

**标注操作：**
- **A**: 添加正向点（在"修正对象"模式下用于mask修正）
- **Del**: 删除当前选中的边界框

> 💡 **提示**: 在对象形状发生显著变化的关键帧使用 **A** 键添加正向点。这可以帮助SAM2在遮挡和形变情况下保持准确追踪。

### 最佳实践 📌

**何时添加标注：**
1. **第0帧**: 对象首次出现时
2. **形变帧**: 对象形状显著变化时
3. **遮挡前后**: 对象被遮挡前和恢复后

**标注策略：**
- 标注帧数量适中（建议：5-10个关键帧）
- 优先标注追踪失败的位置
- 使用"修正对象"模式保持对象ID一致
- 利用实时预览功能即时验证标注质量

**性能优化：**
- 低端GPU使用 **tiny** 或 **small** 模型以获得更快处理速度
- 遇到内存问题时降低视频分辨率
- 关闭不必要的应用程序以释放GPU显存

## 📁 项目结构

```
Micro_Tracker/
├── micro_tracker/                    # 主要应用代码
│   ├── components/                   # UI组件
│   │   ├── custom_widgets.py        # 自定义PyQt5控件
│   │   └── video_widgets.py         # 视频显示与覆盖层
│   ├── config/                       # 配置文件
│   │   └── style.py                  # UI样式
│   ├── controllers/                  # MVC控制器
│   │   ├── filter_controller.py     # 筛选逻辑
│   │   └── processing_controller.py # 视频处理控制
│   ├── threads/                      # 处理线程
│   │   ├── processing_thread.py     # SAM2视频处理
│   │   ├── filter_*.py               # 筛选线程
│   │   └── video_thread.py           # 视频播放
│   ├── ui/                           # UI界面
│   │   ├── main_window.py            # 主窗口
│   │   ├── setup_tab.py              # 标注选项卡
│   │   ├── result_preview_tab.py    # 结果选项卡
│   │   ├── filter_tab.py             # 筛选选项卡
│   │   ├── annotation_manager.py    # 标注管理
│   │   └── ...                       # 其他UI模块
│   └── utils/                        # 工具函数
│       └── preview_manager.py        # 实时mask预览
├── models/                           # 模型目录
│   └── sam2/                         # SAM2模型
│       ├── checkpoints/              # 模型权重文件 (.pt)
│       └── sam2/                     # SAM2源代码
├── utils/                            # 共享工具脚本
│   ├── color.py                      # 颜色工具
│   └── utils.py                      # 通用工具
├── scripts/                          # 处理脚本
│   └── process_video_multiframe.py  # 多帧处理核心
├── assets/                           # 资源文件
│   ├── screenshots/                  # UI截图
│   └── *.mp4                         # 演示视频
├── icons/                            # UI图标
├── main.py                           # 应用入口
├── requirements.txt                  # Python依赖
├── CHANGELOG.md                      # 版本历史
├── README.md                         # 本文件
└── LICENSE                           # Apache 2.0许可证
```

## 🩺 故障排除

### 常见问题 ❓

1.  **启动失败**

    - 检查 Python 版本是否为 3.10+。
    - 确保所有依赖项已正确安装（参照 [安装依赖](#3-安装依赖)）。
    - 验证SAM2安装：`cd models/sam2 && pip install -e .`

2.  **GPU 内存不足**

    - 尝试降低处理视频的分辨率。
    - 减少同时跟踪的目标数量。
    - 使用较小的模型（tiny或small而非large）。
    - 如需要可关闭实时预览（虽然它很轻量）。

3.  **实时预览未显示**

    - 检查日志消息中的预览初始化状态。
    - 验证模型路径配置是否正确。
    - 确保视频已成功加载。
    - 尝试重新加载视频以重新初始化预览。

4.  **跟踪不准确**

    - 确保初始框选的准确性。
    - 在追踪失败处添加更多关键帧标注。
    - 使用 **A** 键添加正向点进行修正。
    - 尝试使用更高质量或更清晰的视频。

5.  **处理速度慢**
    - 确认 GPU 是否正在被程序使用（检查启动或处理时的日志）。
    - 考虑使用性能更强的 GPU。
    - 如可能，减少标注帧数量。
    - 使用较小的SAM2模型版本。

## 📜 许可证

本项目采用 [Apache 2.0 许可证](LICENSE)。

## 🙏 致谢

本项目基于以下优秀项目创建，并从中获得了诸多启发：

- [SAMURAI](https://github.com/yangchris11/samurai)
- [SAM2 (Segment Anything Model 2)](https://github.com/facebookresearch/sam2)
- [Lang2SegTrack](https://github.com/wngkj/Lang2SegTrack)

---

<p align="center"><em>Keep moving, keep thinking!</em></p>
