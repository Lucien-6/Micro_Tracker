# 更新日志 (Changelog)

本文档记录了 Micro_Tracker 项目的所有重要变更。

---

## [v1.1.0-phase1-mvp] - 2025-10-30

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

