# 更新日志 (Changelog)

本文档记录了 Micro_Tracker 项目的所有重要变更。

---

## [v2.3.0] - 2026-01-13

### 🐛 重要修复 (Critical Bug Fix)

#### 修复连续加载视频时旧数据缓存干扰新视频处理的问题

**问题描述：**
当用户完成一个视频的追踪处理后，不关闭 GUI 界面直接加载新视频时，旧视频的标注数据和状态未被完全清理，导致：

- 新视频的对象 ID 不从 0 开始（继承了旧视频的 ID 计数器）
- 旧视频的多帧标注数据可能残留并干扰新视频处理
- 对象注册表和颜色分配混乱
- 预览管理器缓存了旧视频的帧数据

**修复内容：**

1. **新增 `OverlayLayer.reset_all_state()` 方法** (`micro_tracker/components/video_widgets.py`)

   - 清空所有帧的边界框数据 (`bboxes_per_frame`)
   - 清空所有帧的点击标注数据 (`annotations_per_frame`)
   - 重置对象注册表 (`object_registry`) 和 ID 计数器 (`next_available_id`)
   - 重置标注模式、预览 masks、临时点击状态等

2. **新增 `MaskPreviewManager.reset()` 方法** (`micro_tracker/utils/preview_manager.py`)

   - 清除帧缓存和预测线程
   - 保留 predictor 实例避免重复加载模型

3. **新增 `SetupTab.reset_ui_state()` 方法** (`micro_tracker/ui/setup_tab.py`)

   - 重置标注模式 UI 为"新对象"模式
   - 重置提示类型 UI 为"边界框模式"
   - 清空并禁用对象选择器

4. **新增 `MainWindow._reset_for_new_input()` 方法** (`micro_tracker/ui/main_window.py`)

   - 统一调度所有清理操作
   - 停止运行中的处理线程和结果视频线程
   - 调用各组件的重置方法
   - 刷新标注管理器和状态显示

5. **修改 `_load_video()` 和 `_load_image_sequence()` 方法**
   - 在加载新输入源时自动调用 `_reset_for_new_input()`
   - 确保新视频从干净状态开始

**影响范围：**

- 修复了连续处理多个视频时的数据污染问题
- 新视频的对象 ID 现在正确从 0 开始
- 标注管理器正确显示新视频的标注状态
- 实时预览功能正常工作

### 🔄 向后兼容性

- ✅ 完全向后兼容，无数据格式变更
- ✅ 不影响已保存的标注 JSON 文件
- ✅ 不影响处理逻辑和输出格式

---

## [v2.2.0] - 2026-01-05

### 📚 文档更新 (Documentation Update)

**版本说明：**
本版本为文档维护版本，主要完善和更新项目文档内容，确保文档与当前功能状态保持一致。

**更新内容：**

1. **更新 CHANGELOG.md**
   - 添加 v2.2.0 版本条目
   - 规范化版本记录格式

2. **更新 README.md**
   - 更新版本徽章至 v2.2.0
   - 确保功能描述准确反映当前状态

3. **更新使用指南 (guide_tab.py)**
   - 更新版本信息至 v2.2.0
   - 更新发布日期至 2026年1月5日
   - 更新版权信息至 2026年

### 🔄 向后兼容性

- ✅ 完全向后兼容，无代码变更
- ✅ 不影响任何功能和数据格式
- ✅ 纯文档性质更新

---

## [v2.1.0] - 2026-01-04

### ✨ 新增功能 (New Features)

#### 图像序列输入支持

**功能描述：**
新增图像序列作为输入源的支持，用户可以直接从图像文件夹加载帧序列进行目标分割和追踪，无需预先转换为视频格式。

**支持的图像格式：**

- JPEG: `.jpg`, `.jpeg`
- PNG: `.png`
- TIFF: `.tif`, `.tiff`
- BMP: `.bmp`

**核心功能：**

1. **智能文件名排序** (`micro_tracker/utils/input_manager.py`)

   - 支持纯数字命名: `00001.jpg` → 帧 1
   - 支持前缀+数字命名: `frame_00001.png` → 帧 1
   - 支持任意前缀: `img_001.tif` → 帧 1
   - 自动按帧编号升序排列

2. **自动格式转换**

   - SAM2 要求 JPEG 格式输入
   - 非 JPEG 图像自动转换到临时目录
   - 处理完成后自动清理临时文件
   - 原始图像不受影响

3. **UI 集成** (`micro_tracker/ui/setup_tab.py`)

   - 输入类型单选按钮：视频文件 / 图像序列
   - 图像序列模式下选择文件夹
   - 显示图像数量、分辨率、帧率信息
   - 可配置播放帧率（默认 10 FPS）

4. **播放和预览支持** (`micro_tracker/threads/video_thread.py`)
   - `ImageSequenceThread`：图像序列播放线程
   - 支持播放/暂停/跳转
   - 与视频模式保持一致的用户体验

**新增文件：**

- `micro_tracker/utils/input_manager.py` - 输入源抽象和管理

**使用场景：**

- 显微镜逐帧采集的图像序列
- 时间序列拍摄的图像数据
- 已从视频提取的帧图像
- 科研实验的定时拍摄图像

---

### 🐛 修复 (Bug Fixes)

#### 修复视频播放期间预览 mask 停留问题

**问题描述：**
当用户在某一帧标注对象后点击播放，预览 mask 会持续显示在视频的所有帧上，违反了"预览 mask 仅在标注帧显示"的原则。

**修复内容：**

1. **新增静默帧切换方法** (`micro_tracker/components/video_widgets.py`)

   - 添加 `set_current_frame_silent(frame_idx)` 方法
   - 视频播放期间使用此方法更新帧索引
   - 自动清除 `preview_masks`
   - 同步边界框显示
   - 不弹出对话框、不询问未保存的临时点击

2. **更新帧滑块回调** (`micro_tracker/ui/main_window.py`)
   - `update_frame_slider()` 现在调用 `set_current_frame_silent()`
   - 确保视频播放期间正确清除预览

**影响范围：**

- 修复了视频播放时的视觉干扰问题
- 不影响标注数据和处理逻辑
- 提升了用户体验

---

### 🔧 改进 (Improvements)

- **输入源抽象**：统一视频和图像序列的接口，便于未来扩展
- **临时文件管理**：自动清理格式转换产生的临时文件

---

### 🔄 向后兼容性

- ✅ 完全向后兼容现有视频输入工作流
- ✅ 不影响标注数据格式
- ✅ 不影响处理逻辑和输出格式

---

## [v2.0.2] - 2025-11-01

### ✨ UI/UX 改进 (UI/UX Enhancement)

#### 增强 Refinement 模式符合 SAM2 官方最佳实践

**背景：**
根据 SAM2 官方文档（`video_predictor_example.ipynb`），refinement 过程推荐使用点击提示而非边界框，因为：

- 边界框在 tracking 开始后添加时，SAM2 可能无法很好地整合
- 点击提示更适合精细化修正

**改进内容：**

1. **自动切换提示模式** (`micro_tracker/ui/setup_tab.py`)

   - 切换到修正对象模式时，自动切换到点击模式
   - 禁用边界框模式选项（防止误操作）
   - 切换回新对象模式时，自动恢复边界框选项

2. **阻止 Refinement 模式下的 Box 绘制** (`micro_tracker/components/video_widgets.py`)

   - 修正模式下尝试绘制边界框时显示警告提示
   - 强制用户使用点击提示
   - 提示信息："⚠️ 修正模式下不能绘制新的边界框，请使用点击提示（符合 SAM2 官方规范）"

3. **标注列表显示优化** (`micro_tracker/ui/annotation_manager.py`)

   - 支持显示纯点击标注（无边界框的帧）
   - 合并 bbox 和 refinement 数据源
   - 正确统计包含点击标注的对象数量

4. **用户文档更新** (`micro_tracker/ui/annotation_manager.py`)
   - 帮助对话框增加 SAM2 官方规范说明
   - 明确标注修正模式的约束
   - 添加视觉高亮警告

**用户体验提升：**

- ✅ 减少误操作：自动模式切换 + UI 约束
- ✅ 符合最佳实践：引导用户使用 SAM2 推荐方式
- ✅ 透明反馈：清晰的警告和提示信息
- ✅ 完整支持：纯点击标注也能在 UI 中正常显示

**兼容性：**

- ✅ 不影响现有标注数据
- ✅ 不影响视频处理逻辑
- ✅ 纯 UI 层改进，无破坏性变更

---

## [v2.0.1] - 2025-11-01

### 🐛 重要修复 (Critical Fix)

#### 修复 SAM2 混合提示处理方式，符合官方 API 规范

**问题描述：**
当同时使用边界框(box)和点击(points)进行 refinement 时，之前的实现分两次调用`add_new_points_or_box` API，不符合 SAM2 官方推荐方式，可能导致：

- 精细化 refinement 效果打折扣
- 跨帧一致性问题
- 复杂形状和遮挡场景下的分割质量下降

**修复内容：**

- **核心修改**：`scripts/process_video_multiframe.py` (第 140-179 行)
  - 将分两次调用改为**一次性调用**`add_new_points_or_box`
  - Box 和 points 在同一个 API 调用中传入（如果都存在）
  - 始终使用`clear_old_points=True`（符合 SAM2 API 约定）
  - Box 会在 SAM2 内部自动转换为 2 个特殊点(标签 2 和 3)，然后与用户点击拼接
- **技术细节**：
  - SAM2 的 Transformer Encoder 现在能在同一个 attention 层中处理所有提示
  - Box 和 points 形成完整的语义单元，而非两次独立的"修正"
  - 提升了 refinement 质量和 temporal consistency
- **文档更新**：
  - 更新函数 docstring，添加"Prompt Handling Strategy"说明
  - 明确标注符合 SAM2 官方规范的实现方式
  - 添加参考：`models/sam2/video_predictor_example.ipynb` (Cell 46)

**测试验证：**

- ✅ API 调用逻辑验证测试通过（5 个测试用例）
- ✅ 混合提示（box + points）现在在一次调用中传入
- ✅ 所有情况都使用`clear_old_points=True`

**兼容性：**

- ✅ 向后兼容：现有标注 JSON 文件无需修改
- ✅ 数据结构不变：UI 和标注管理不受影响
- ✅ 实时预览功能已正确实现，无需修改

**影响范围：**

- 主要影响：视频处理的 refinement 质量（提升）
- 不影响：UI 界面、标注数据格式、导入导出功能

**参考资料：**

- SAM2 官方教程：`models/sam2/video_predictor_example.ipynb`
- SAM2 源码：`models/sam2/sam2/sam2_video_predictor.py` (L294-318)

---

## [v2.0] - 2025-10-31

### 🎉 正式发布 (Major Release)

此版本标志着 Micro Tracker 的重大里程碑，完整实现了多帧智能标注和实时预览功能，提供了生产级别的显微视频分析能力。

### ✨ 核心功能亮点

#### 1. 多帧智能标注系统

- **双模式标注**：
  - 🆕 新对象模式：自动分配唯一 ID 和固定颜色
  - ✏️ 修正对象模式：为已有对象添加关键帧标注
- **对象颜色管理**：
  - 每个对象 ID 映射固定颜色，跨帧保持一致
  - 正在修正的对象用金色虚线高亮显示
  - 边界框粗细和样式优化，提升可视性

#### 2. 实时预览功能

- **SAM2 集成**：添加标注后自动生成 mask 预览
- **智能缓存**：帧切换时自动恢复预览状态
- **性能优化**：懒加载预览管理器，减少启动时间
- **降级策略**：GPU 不可用时自动降级为纯标注模式

#### 3. 标注管理面板

- **标注列表**：显示所有已标注帧（帧索引 + 对象数量）
- **快速跳转**：点击按钮快速定位到指定标注帧
- **批量操作**：删除指定帧标注或清除所有标注
- **数据持久化**：
  - 导出标注为 JSON 格式
  - 导入 JSON 恢复标注数据
  - 与视频项目解耦，便于协作

#### 4. 多帧 SAM2 处理引擎

- **分段前向传播**：
  - 将标注帧作为段边界
  - 在每个段的起始帧应用 SAM2 提示
  - 段间独立处理，避免状态累积
- **提示策略优化**：
  - 每个标注帧调用 `add_new_points_or_box`
  - 正确设置 `clear_old_points=True`
  - 避免状态冲突和错误累积

### 🔧 架构改进 (Refactored)

- **统一多帧模式**：
  - 移除单帧/多帧判断逻辑，简化代码约 70 行
  - 单帧标注现在视为多帧的特例（只有 1 个标注帧）
  - UI 简化：移除"多帧标注模式"指示器
- **代码重构**：
  - 优化 `OverlayLayer` 数据结构
  - 统一标注状态管理逻辑
  - 改进事件处理和信号连接

### 🐛 修复 (Fixed)

- **多段处理冲突**：

  - 每个段开始前重新初始化 `inference_state`
  - 修复 `KeyError: 'best_iou_score'`
  - 修复 `AssertionError: all_consolidated_frame_inds == input_frames_inds`

- **SAM2 box prompt 错误**：

  - 正确设置 `clear_old_points=True`
  - 修复 `RuntimeError: cannot add box without clearing old points`
  - 修复 `RuntimeError: No points are provided`

- **进度回调签名**：

  - 创建统一的 `multiframe_progress_callback`
  - 修复 `TypeError: missing 1 required positional argument 'total'`

- **帧切换同步**：
  - 修复 `set_current_frame` 在相同帧索引下不同步的 bug
  - 优化边界框同步逻辑

### 📚 文档更新

- **使用指南**：完整重写多帧标注和实时预览章节
- **README**：更新功能特性和使用流程说明
- **CHANGELOG**：整理所有版本历史

### 🎯 用户体验提升

- **操作提示**：
  - 日志区分"新对象"和"修正对象"操作
  - 实时显示已标注帧数和对象数量
  - 标注帧用绿色高亮显示
- **最佳实践指引**：
  - 在使用指南中明确标注时机
  - 建议关键帧数量（5-10 个）
  - 提供标注策略说明

### ⚙️ 技术细节

**修改的核心文件**：

- `micro_tracker/components/video_widgets.py` - 数据结构和渲染逻辑
- `micro_tracker/ui/setup_tab.py` - 标注模式 UI 和管理面板
- `micro_tracker/ui/main_window.py` - 主窗口集成和事件处理
- `micro_tracker/controllers/processing_controller.py` - 处理逻辑
- `micro_tracker/threads/processing_thread.py` - 多帧处理引擎
- `micro_tracker/utils/preview_manager.py` - 实时预览管理器

**新增文件**：

- `micro_tracker/ui/annotation_manager.py` - 标注管理 UI 组件

### 🔄 向后兼容性

- ✅ 完全向后兼容旧版本标注格式
- ✅ 自动转换列表格式为字典格式
- ✅ 支持纯单帧标注工作流

### 🚀 性能优化

- 懒加载预览管理器，减少初始化时间
- 使用定时器防抖优化状态更新
- 预览 mask 智能缓存和恢复

### 📊 测试覆盖

- ✅ 多帧标注数据结构测试
- ✅ 对象 ID 管理测试
- ✅ 标注导入/导出测试
- ✅ 边界框向后兼容性测试

### 🎓 致谢

感谢以下项目的启发和支持：

- [SAM2 (Segment Anything Model 2)](https://github.com/facebookresearch/sam2)
- [SAMURAI](https://github.com/yangchris11/samurai)

---

## [v1.2.0-phase2] - 2025-10-30 (开发版本)

### 🔧 架构改进 (Refactored - 2025-10-30)

- **统一使用多帧处理模式**
  - 移除单帧/多帧模式判断和切换逻辑
  - 单帧标注现在视为多帧的特例（只有 1 个标注帧）
  - 代码简化约 70 行，逻辑更清晰
  - 旧格式列表自动转换为字典 `{0: bbox_list}`
  - UI 简化：移除"多帧标注模式"指示器（因为总是多帧）

### 🐛 紧急修复 (Hotfix - 2025-10-30)

- **修复多段处理时的 inference_state 冲突**

  - 在每个段开始前重新初始化 inference_state（seg_idx > 0）
  - 确保段与段之间相互独立，避免状态累积
  - 修复了错误: `KeyError: 'best_iou_score'`
  - 修复了错误: `AssertionError: all_consolidated_frame_inds == input_frames_inds`

- **修复 SAM2 box prompt 参数错误**

  - `clear_old_points` 必须设置为 `True` 才能添加 box 提示
  - 修复了运行时错误: `cannot add box without clearing old points`
  - 修复了错误: `RuntimeError: No points are provided; please add points first`

- **修复进度回调函数签名不匹配**
  - 创建统一的 `multiframe_progress_callback`（接受消息字符串）
  - 修复了运行时错误: `TypeError: missing 1 required positional argument 'total'`

### ✨ 新增功能 (Added)

- **真正的多帧 SAM2 提示处理**

  - 在每个标注帧调用 SAM2 的 `add_new_points_or_box`
  - 实现分段前向传播策略
  - 显著提升追踪质量（特别是对象形变、遮挡场景）

- **智能对象 ID 管理**

  - 新对象模式：自动分配新 ID
  - 修正对象模式：为已有对象添加新帧标注
  - 对象颜色固定映射（同一对象在不同帧用相同颜色）
  - 金色虚线高亮正在修正的对象

- **标注管理 UI**
  - 标注列表：查看所有标注帧和对象数
  - 快速跳转：点击跳转到任意标注帧
  - 批量删除：删除指定帧或所有标注
  - 导入/导出：JSON 格式标注文件

### 🔧 改进 (Changed)

- 处理线程自动检测标注模式（单帧/多帧）
- 日志输出更详细（显示处理段、对象 ID 等信息）
- UI 布局优化，添加模式选择器和标注管理器

### 🐛 修复 (Fixed)

- 无（Phase 2 基于稳定的 Phase 1 MVP）

### ⚠️ 使用建议

**何时添加标注**:

1. 第 0 帧：对象首次出现
2. 形变帧：对象形状显著变化
3. 遮挡前后：对象被遮挡前和恢复后

**最佳实践**:

- 标注帧不宜过多（建议 5-10 个关键帧）
- 优先标注追踪失败的位置
- 使用修正模式保持对象 ID 一致

---

## [v1.1.0-phase1-mvp] - 2025-10-30

### 🐛 紧急修复 (Hotfix - 2025-10-30)

- **修复 `bbox_process` 函数兼容性问题**
  - 函数现在支持 5 值格式 `[x1, y1, x2, y2, obj_id]`
  - 保持对旧 4 值格式的向后兼容
  - 修复了运行时错误: `ValueError: too many values to unpack (expected 4)`
  - 添加了完整的单元测试覆盖

### ✨ 新增功能 (Added)

- **多帧标注支持（Phase 1 MVP）**
  - 用户现在可以在视频的任意帧添加边界框标注
  - 边界框随帧切换自动显示/隐藏
  - 已标注帧数实时统计显示
  - UI 增加了"多帧标注模式"指示器

### 🔧 改进 (Changed)

- 重构了 `OverlayLayer` 数据结构，使用字典存储多帧标注
- 更新了处理控制器以支持多帧标注数据
- 改进了日志显示，区分单帧和多帧标注模式
- 操作说明更新以反映多帧功能

### 🐛 修复 (Fixed)

- 修复了 `set_current_frame` 在相同帧索引下不同步的 bug
- 修复了 `_sync_bboxes_from_current_frame` 的优化逻辑问题

### ⚠️ 已知限制 (Known Limitations)

- **Phase 1 MVP 限制**：当前版本在处理时仅使用第一个标注帧作为起点
- 完整的多帧 SAM2 提示处理功能计划在 Phase 2 中实现

### 🧪 测试 (Testing)

- 添加了 8 个单元测试，验证多帧标注核心功能
- 所有测试通过，覆盖率良好

### 🔄 向后兼容性 (Backward Compatibility)

- ✅ 完全向后兼容，单帧标注模式仍然有效
- 旧版本数据格式自动转换为新格式

### 📝 技术细节 (Technical Details)

**修改的文件：**

- `micro_tracker/components/video_widgets.py` - 核心数据结构
- `micro_tracker/ui/main_window.py` - UI 集成
- `micro_tracker/ui/setup_tab.py` - UI 增强
- `micro_tracker/controllers/processing_controller.py` - 处理逻辑
- `micro_tracker/threads/processing_thread.py` - 线程处理

**新增文件：**

- `tests/test_multi_frame_overlay.py` - 单元测试

---

## [v1.0.0] - 2025-01-XX

### ✨ 初始版本

- 基于 SAM2 的视频对象分割和追踪
- 支持单帧标注
- 视频播放和预览
- 掩码导出功能
- 结果筛选功能

---

## 格式说明

- ✨ 新增功能
- 🔧 改进
- 🐛 修复
- ⚠️ 已知限制
- 🧪 测试
- 🔄 向后兼容性
- 📝 技术细节
- 🗑️ 废弃
- 🔥 移除
