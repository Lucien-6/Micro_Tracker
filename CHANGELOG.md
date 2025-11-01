# 更新日志 (Changelog)

本文档记录了 Micro_Tracker 项目的所有重要变更。

---

## [v2.0.1] - 2025-11-01

### 🐛 重要修复 (Critical Fix)

#### 修复SAM2混合提示处理方式，符合官方API规范

**问题描述：**
当同时使用边界框(box)和点击(points)进行refinement时，之前的实现分两次调用`add_new_points_or_box` API，不符合SAM2官方推荐方式，可能导致：
- 精细化refinement效果打折扣
- 跨帧一致性问题
- 复杂形状和遮挡场景下的分割质量下降

**修复内容：**
- **核心修改**：`scripts/process_video_multiframe.py` (第140-179行)
  - 将分两次调用改为**一次性调用**`add_new_points_or_box`
  - Box和points在同一个API调用中传入（如果都存在）
  - 始终使用`clear_old_points=True`（符合SAM2 API约定）
  - Box会在SAM2内部自动转换为2个特殊点(标签2和3)，然后与用户点击拼接
  
- **技术细节**：
  - SAM2的Transformer Encoder现在能在同一个attention层中处理所有提示
  - Box和points形成完整的语义单元，而非两次独立的"修正"
  - 提升了refinement质量和temporal consistency
  
- **文档更新**：
  - 更新函数docstring，添加"Prompt Handling Strategy"说明
  - 明确标注符合SAM2官方规范的实现方式
  - 添加参考：`models/sam2/video_predictor_example.ipynb` (Cell 46)

**测试验证：**
- ✅ API调用逻辑验证测试通过（5个测试用例）
- ✅ 混合提示（box + points）现在在一次调用中传入
- ✅ 所有情况都使用`clear_old_points=True`

**兼容性：**
- ✅ 向后兼容：现有标注JSON文件无需修改
- ✅ 数据结构不变：UI和标注管理不受影响
- ✅ 实时预览功能已正确实现，无需修改

**影响范围：**
- 主要影响：视频处理的refinement质量（提升）
- 不影响：UI界面、标注数据格式、导入导出功能

**参考资料：**
- SAM2官方教程：`models/sam2/video_predictor_example.ipynb`
- SAM2源码：`models/sam2/sam2/sam2_video_predictor.py` (L294-318)

---

## [v2.0] - 2025-10-31

### 🎉 正式发布 (Major Release)

此版本标志着 Micro Tracker 的重大里程碑，完整实现了多帧智能标注和实时预览功能，提供了生产级别的显微视频分析能力。

### ✨ 核心功能亮点

#### 1. 多帧智能标注系统
- **双模式标注**：
  - 🆕 新对象模式：自动分配唯一ID和固定颜色
  - ✏️ 修正对象模式：为已有对象添加关键帧标注
- **对象颜色管理**：
  - 每个对象ID映射固定颜色，跨帧保持一致
  - 正在修正的对象用金色虚线高亮显示
  - 边界框粗细和样式优化，提升可视性
  
#### 2. 实时预览功能
- **SAM2集成**：添加标注后自动生成mask预览
- **智能缓存**：帧切换时自动恢复预览状态
- **性能优化**：懒加载预览管理器，减少启动时间
- **降级策略**：GPU不可用时自动降级为纯标注模式

#### 3. 标注管理面板
- **标注列表**：显示所有已标注帧（帧索引 + 对象数量）
- **快速跳转**：点击按钮快速定位到指定标注帧
- **批量操作**：删除指定帧标注或清除所有标注
- **数据持久化**：
  - 导出标注为JSON格式
  - 导入JSON恢复标注数据
  - 与视频项目解耦，便于协作

#### 4. 多帧SAM2处理引擎
- **分段前向传播**：
  - 将标注帧作为段边界
  - 在每个段的起始帧应用SAM2提示
  - 段间独立处理，避免状态累积
- **提示策略优化**：
  - 每个标注帧调用 `add_new_points_or_box`
  - 正确设置 `clear_old_points=True`
  - 避免状态冲突和错误累积

### 🔧 架构改进 (Refactored)

- **统一多帧模式**：
  - 移除单帧/多帧判断逻辑，简化代码约70行
  - 单帧标注现在视为多帧的特例（只有1个标注帧）
  - UI简化：移除"多帧标注模式"指示器
  
- **代码重构**：
  - 优化 `OverlayLayer` 数据结构
  - 统一标注状态管理逻辑
  - 改进事件处理和信号连接

### 🐛 修复 (Fixed)

- **多段处理冲突**：
  - 每个段开始前重新初始化 `inference_state`
  - 修复 `KeyError: 'best_iou_score'`
  - 修复 `AssertionError: all_consolidated_frame_inds == input_frames_inds`

- **SAM2 box prompt错误**：
  - 正确设置 `clear_old_points=True`
  - 修复 `RuntimeError: cannot add box without clearing old points`
  - 修复 `RuntimeError: No points are provided`

- **进度回调签名**：
  - 创建统一的 `multiframe_progress_callback`
  - 修复 `TypeError: missing 1 required positional argument 'total'`

- **帧切换同步**：
  - 修复 `set_current_frame` 在相同帧索引下不同步的bug
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
  - 建议关键帧数量（5-10个）
  - 提供标注策略说明

### ⚙️ 技术细节

**修改的核心文件**：
- `micro_tracker/components/video_widgets.py` - 数据结构和渲染逻辑
- `micro_tracker/ui/setup_tab.py` - 标注模式UI和管理面板
- `micro_tracker/ui/main_window.py` - 主窗口集成和事件处理
- `micro_tracker/controllers/processing_controller.py` - 处理逻辑
- `micro_tracker/threads/processing_thread.py` - 多帧处理引擎
- `micro_tracker/utils/preview_manager.py` - 实时预览管理器

**新增文件**：
- `micro_tracker/ui/annotation_manager.py` - 标注管理UI组件

### 🔄 向后兼容性

- ✅ 完全向后兼容旧版本标注格式
- ✅ 自动转换列表格式为字典格式
- ✅ 支持纯单帧标注工作流

### 🚀 性能优化

- 懒加载预览管理器，减少初始化时间
- 使用定时器防抖优化状态更新
- 预览mask智能缓存和恢复

### 📊 测试覆盖

- ✅ 多帧标注数据结构测试
- ✅ 对象ID管理测试
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
  - 单帧标注现在视为多帧的特例（只有1个标注帧）
  - 代码简化约70行，逻辑更清晰
  - 旧格式列表自动转换为字典 `{0: bbox_list}`
  - UI简化：移除"多帧标注模式"指示器（因为总是多帧）

### 🐛 紧急修复 (Hotfix - 2025-10-30)

- **修复多段处理时的inference_state冲突**
  - 在每个段开始前重新初始化inference_state（seg_idx > 0）
  - 确保段与段之间相互独立，避免状态累积
  - 修复了错误: `KeyError: 'best_iou_score'`
  - 修复了错误: `AssertionError: all_consolidated_frame_inds == input_frames_inds`

- **修复SAM2 box prompt参数错误**
  - `clear_old_points` 必须设置为 `True` 才能添加box提示
  - 修复了运行时错误: `cannot add box without clearing old points`
  - 修复了错误: `RuntimeError: No points are provided; please add points first`

- **修复进度回调函数签名不匹配**
  - 创建统一的 `multiframe_progress_callback`（接受消息字符串）
  - 修复了运行时错误: `TypeError: missing 1 required positional argument 'total'`

### ✨ 新增功能 (Added)

- **真正的多帧SAM2提示处理**
  - 在每个标注帧调用SAM2的 `add_new_points_or_box`
  - 实现分段前向传播策略
  - 显著提升追踪质量（特别是对象形变、遮挡场景）

- **智能对象ID管理**
  - 新对象模式：自动分配新ID
  - 修正对象模式：为已有对象添加新帧标注
  - 对象颜色固定映射（同一对象在不同帧用相同颜色）
  - 金色虚线高亮正在修正的对象

- **标注管理UI**
  - 标注列表：查看所有标注帧和对象数
  - 快速跳转：点击跳转到任意标注帧
  - 批量删除：删除指定帧或所有标注
  - 导入/导出：JSON格式标注文件

### 🔧 改进 (Changed)

- 处理线程自动检测标注模式（单帧/多帧）
- 日志输出更详细（显示处理段、对象ID等信息）
- UI布局优化，添加模式选择器和标注管理器

### 🐛 修复 (Fixed)

- 无（Phase 2基于稳定的Phase 1 MVP）

### ⚠️ 使用建议

**何时添加标注**:
1. 第0帧：对象首次出现
2. 形变帧：对象形状显著变化
3. 遮挡前后：对象被遮挡前和恢复后

**最佳实践**:
- 标注帧不宜过多（建议5-10个关键帧）
- 优先标注追踪失败的位置
- 使用修正模式保持对象ID一致

---

## [v1.1.0-phase1-mvp] - 2025-10-30

### 🐛 紧急修复 (Hotfix - 2025-10-30)

- **修复 `bbox_process` 函数兼容性问题**
  - 函数现在支持5值格式 `[x1, y1, x2, y2, obj_id]`
  - 保持对旧4值格式的向后兼容
  - 修复了运行时错误: `ValueError: too many values to unpack (expected 4)`
  - 添加了完整的单元测试覆盖

### ✨ 新增功能 (Added)

- **多帧标注支持（Phase 1 MVP）**
  - 用户现在可以在视频的任意帧添加边界框标注
  - 边界框随帧切换自动显示/隐藏
  - 已标注帧数实时统计显示
  - UI增加了"多帧标注模式"指示器

### 🔧 改进 (Changed)

- 重构了 `OverlayLayer` 数据结构，使用字典存储多帧标注
- 更新了处理控制器以支持多帧标注数据
- 改进了日志显示，区分单帧和多帧标注模式
- 操作说明更新以反映多帧功能

### 🐛 修复 (Fixed)

- 修复了 `set_current_frame` 在相同帧索引下不同步的bug
- 修复了 `_sync_bboxes_from_current_frame` 的优化逻辑问题

### ⚠️ 已知限制 (Known Limitations)

- **Phase 1 MVP 限制**：当前版本在处理时仅使用第一个标注帧作为起点
- 完整的多帧SAM2提示处理功能计划在 Phase 2 中实现

### 🧪 测试 (Testing)

- 添加了8个单元测试，验证多帧标注核心功能
- 所有测试通过，覆盖率良好

### 🔄 向后兼容性 (Backward Compatibility)

- ✅ 完全向后兼容，单帧标注模式仍然有效
- 旧版本数据格式自动转换为新格式

### 📝 技术细节 (Technical Details)

**修改的文件：**
- `micro_tracker/components/video_widgets.py` - 核心数据结构
- `micro_tracker/ui/main_window.py` - UI集成
- `micro_tracker/ui/setup_tab.py` - UI增强
- `micro_tracker/controllers/processing_controller.py` - 处理逻辑
- `micro_tracker/threads/processing_thread.py` - 线程处理

**新增文件：**
- `tests/test_multi_frame_overlay.py` - 单元测试

---

## [v1.0.0] - 2025-01-XX

### ✨ 初始版本

- 基于SAM2的视频对象分割和追踪
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

