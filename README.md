# Micro_Tracker

Micro_Tracker 是一个基于 SAM2 模型的显微镜图像/视频分析工具，专为微观生物体和颗粒的跟踪和分析而设计。该应用提供直观的用户界面，使研究人员能够轻松地标记、跟踪和分析显微镜下的目标物体。

## 功能特点

- **实时目标跟踪**：利用 SAM2（Segment Anything Model 2）实现高精度的目标分割和跟踪
- **手动标注**：支持手动框选感兴趣区域(ROI)
- **视频分析**：处理显微镜视频并生成带有标记和轨迹的输出视频
- **数据提取**：提取目标物体的位置、大小、形状等关键参数
- **掩膜导出**：将分割结果保存为掩膜图像，便于后续分析
- **筛选功能**：根据尺寸、位置、形状等条件筛选目标物体
- **数据统计**：对检测到的物体进行统计分析，生成可视化图表

## 系统要求

- Windows 10/11 或 Linux 系统
- Python 3.8+
- NVIDIA GPU (至少 4GB 显存)和 CUDA 11.7+（推荐）

## 安装指南

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/Micro_Tracker.git
cd Micro_Tracker
```

### 2. 创建虚拟环境(推荐)

```bash
# 使用conda
conda create -n microtracker python=3.8
conda activate microtracker

# 或使用venv
python -m venv microtracker_env
# Windows
microtracker_env\Scripts\activate
# Linux/Mac
source microtracker_env/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 下载模型

SAM2 模型文件需要单独下载：

1. 访问[SAM2 官方仓库](https://github.com/facebookresearch/segment-anything)下载模型文件
2. 将下载的模型文件(.pth)放置在`models/sam2/checkpoints`目录下

## 使用方法

### 启动应用

```bash
python SAM_tracker.py
```

### 主要功能使用流程

#### 1. 视频跟踪

1. 点击"浏览"按钮选择显微镜视频文件
2. 设置输出目录和参数
3. 在视频第一帧上框选要跟踪的目标（可以框选多个目标）
4. 点击"开始处理"按钮
5. 处理完成后，可以在结果标签页预览输出视频和查看分析结果

#### 2. 掩膜筛选

1. 进入"掩膜筛选"标签页
2. 选择包含掩膜文件的目录
3. 设置筛选参数（如面积范围、瞬时速率等）
4. 点击"应用筛选"按钮
5. 查看筛选结果和统计信息
6. 点击"保存结果"导出筛选后的数据

### 快捷键

- **空格键**：播放/暂停视频
- **→**：下一帧
- **←**：上一帧
- **Del**：删除当前选中的框

## 文件结构

```
Micro_Tracker/
├── SAM_tracker.py         # 主程序
├── requirements.txt       # 依赖列表
├── models/                # 模型文件夹
│   └── sam2/              # SAM2模型
├── utils/                 # 工具函数
├── scripts/               # 处理脚本
├── assets/                # 资源文件
└── icons/                 # 界面图标
```

## 故障排除

### 常见问题

1. **启动失败**

   - 检查 Python 版本是否为 3.8+
   - 确保所有依赖已正确安装

2. **GPU 内存不足**

   - 降低处理视频的分辨率
   - 减少同时跟踪的目标数量

3. **跟踪不准确**

   - 确保初始框选的准确性
   - 尝试使用更高质量的视频

4. **处理速度慢**
   - 检查 GPU 是否正在使用
   - 考虑使用性能更好的 GPU

## 许可证

本项目采用[LICENSE](LICENSE)文件中描述的许可证。
