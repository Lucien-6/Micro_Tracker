# 更新日志 (Changelog)

本文档记录了 Micro_Tracker 项目的所有重要变更。

---

## [v1.2.0-phase2] - 2025-10-30

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

