# 更新日志 (Changelog)

本文档记录了 Micro_Tracker 项目的所有重要变更。

---

## [v2.7.0] - 2026-02-04

### 📖 文档系统重大升级 (Documentation System Overhaul)

#### 使用指南 HTML 化改造

**改进目标：**
提升使用指南的可读性和易用性，采用专业的 HTML 网页形式，提供更好的导航和阅读体验。

**核心改进内容：**

1. **删除使用指南标签页**

   - 移除顶部的"使用指南"标签页（原通过 `guide_tab.py` 实现）
   - 简化主界面标签页为 3 个：分割追踪、结果预览、筛选过滤
   - 减少界面复杂度，聚焦核心功能

2. **创建专业 HTML 使用指南**

   - 新文件：`docs/user_guide.html`
   - 采用外部浏览器打开方式，提供更自由的阅读体验
   - 完整独立的 HTML 文档，无外部依赖

3. **HTML 文档核心特性**

   **导航系统：**

   - 左侧固定侧边栏导航（280px 宽）
   - 11 个主要章节，2 个可折叠章节（标注教程、筛选过滤）
   - 点击章节平滑滚动跳转
   - 滚动同步高亮当前阅读章节
   - 章节自动展开/折叠功能

   **暗色模式：**

   - 右上角切换按钮（🌙 ↔ ☀️）
   - localStorage 保存用户偏好
   - 明亮模式：白色背景 + 蓝色主题
   - 暗色模式：深蓝灰背景 (#1a1d29) + 柔和暖白文字
   - 所有元素适配两种主题

   **视觉风格：**

   - 技术文档风格 + 适度 emoji
   - 学术深蓝配色方案（#1976D2，与 GUI 保持一致）
   - 清晰的层级结构
   - 表格斑马纹背景
   - 信息框彩色左边框（提示/警告/成功）
   - 键盘快捷键徽章样式

   **响应式设计：**

   - 自适应不同屏幕尺寸
   - 小屏幕下侧边栏自动转为顶部导航
   - 内容区域最大宽度 900px，保持最佳阅读宽度

4. **内容整合与精简**

   - 将原标注说明内容完整合并到使用指南
   - 新增"标注教程"独立章节（包含 5 个子章节）
   - 删除重复内容（快捷键表格、模式说明等）
   - 按流程组织内容（快速开始 → 标注 → 处理 → 筛选 → 参考）
   - 总计 11 个主要章节，内容更系统化

5. **按钮改造**

   - 标注管理面板的"标注说明"按钮改为"使用指南"
   - 按钮文本：`"使用指南"`
   - 按钮提示：`"打开完整的使用指南（浏览器）"`
   - 点击行为：在默认浏览器中打开 `docs/user_guide.html`

**技术实现：**

1. **HTML/CSS/JavaScript 实现** (`docs/user_guide.html`)

   - 纯手写 CSS，无外部框架依赖
   - 使用 CSS 变量管理明暗主题颜色
   - JavaScript 实现交互功能：
     - 侧边栏折叠/展开
     - 平滑滚动跳转
     - 滚动同步高亮（Intersection Observer API）
     - 暗色模式切换和保存
   - 总代码量：约 800 行（HTML+CSS+JS）

2. **Python 代码修改**

   **修改文件：** `micro_tracker/ui/annotation_manager.py`

   - 添加导入：`import webbrowser`
   - 修改按钮初始化（第 298-302 行）
   - 删除 `show_help_dialog()` 方法（255 行代码）
   - 新增 `open_user_guide()` 方法：
     - 构建 HTML 文件绝对路径
     - 检查文件是否存在
     - 使用 `webbrowser.open()` 在浏览器打开
     - 提供友好的错误处理

   **修改文件：** `micro_tracker/ui/main_window.py`

   - 删除 `GuideTab` 导入（第 19 行）
   - 删除 `guide_tab` 初始化（第 95 行）
   - 删除 `addTab("使用指南")` 调用（第 101 行）

   **删除文件：** `micro_tracker/ui/guide_tab.py`

   - 完全移除旧的使用指南标签页实现（414 行代码）

**影响范围：**

- ✅ 用户体验大幅提升：专业的文档导航和阅读体验
- ✅ 界面简化：标签页数量从 4 个减少到 3 个
- ✅ 内容整合：标注说明完全合并到使用指南
- ✅ 现代化：支持暗色模式、平滑滚动等现代特性
- ✅ 独立性：HTML 文档可独立分发和查看
- ✅ 不影响任何业务逻辑和数据处理
- ✅ 完全向后兼容

**用户体验提升：**

- ✅ 导航便捷：侧边栏目录一目了然，快速定位
- ✅ 阅读舒适：暗色模式保护视力，长时间阅读更舒适
- ✅ 内容完整：所有使用说明和标注教程集中在一处
- ✅ 查找容易：11 个清晰章节，逻辑结构更合理
- ✅ 访问灵活：可在浏览器中自由缩放、搜索、打印

**技术细节：**

**新增文件：**

- `docs/user_guide.html` - 800 行专业 HTML 文档

**修改的核心文件：**

- `micro_tracker/ui/annotation_manager.py` - 按钮功能改造
- `micro_tracker/ui/main_window.py` - 移除使用指南标签页

**删除的文件：**

- `micro_tracker/ui/guide_tab.py` - 旧实现完全移除

---

## [v2.6.0] - 2026-02-04

### 🎨 GUI 优化升级 (GUI Enhancement)

#### 全面的界面美化和用户体验提升

**优化目标：**
提升 GUI 的美观程度和易用性，采用学术专业风格，增强交互反馈，优化视觉一致性。

**核心改进内容：**

1. **配色方案升级 - 学术深蓝色系**

   - 主色调：`#0D47A1`（牛津蓝）- 专业且稳重
   - 辅助色：`#1565C0`（皇家蓝）- hover 状态
   - 浅色：`#E1F5FE`（冰蓝）- 选中背景
   - 深色：`#01579B`（午夜蓝）- pressed 状态
   - 所有交互元素（按钮、复选框、滑块、标签页）统一应用新配色
   - 提升专业感和品牌识别度

2. **圆角半径统一规范**

   - 小组件（4px）：输入框、下拉框、复选框、小按钮
   - 大组件（6px）：分组框、大按钮、进度条、日志区域
   - 视觉一致性显著提升，界面更加和谐

3. **布局间距优化**

   - 主要功能区间距增加到 20-25px
   - 文件选择 ↔ 参数设置：25px
   - 参数设置 ↔ 处理进度：25px
   - 筛选条件各组间：20-25px
   - 改善视觉呼吸感，信息层次更清晰

4. **Material Design 波纹效果**

   - **新增组件**：`RippleButton`（所有按钮）
   - 点击时显示从点击点扩散的波纹动画
   - 动画参数：
     - 扩散时长：600ms
     - 缓动曲线：OutCubic
     - 波纹颜色：白色，透明度 40%→0%
   - 应用范围：所有按钮（浏览、开始、应用、保存、跳转、删除等）
   - 提升交互流畅感和现代感

5. **输入框焦点发光效果**

   - **新增组件**：`FocusGlowLineEdit`（所有输入框）
   - 获得焦点时显示蓝色发光效果
   - 发光参数：
     - 颜色：`#0D47A1`
     - 模糊半径：6px
     - 透明度：60%
   - 使用 QGraphicsDropShadowEffect 实现
   - 明确当前输入位置，降低误操作

6. **标注模式选中强调**

   - 单选按钮（新对象/修正对象、边界框/点击模式）
   - 选中状态：
     - 背景：`#E1F5FE`（冰蓝）
     - 文字：`#01579B`（午夜蓝）
     - 边框：2px `#0D47A1`
     - 圆角：4px
     - 字重：bold
   - 视觉状态清晰，减少模式混淆

7. **进度条波浪动画**

   - **新增组件**：`AnimatedProgressBar`
   - 水平波浪渐变滚动效果
   - 动画参数：
     - 波长：40px
     - 滚动周期：1.5 秒
     - 渐变：浅绿 → 深绿 → 浅绿
   - 仅在 0% < 进度 < 100%时显示动画
   - 提供视觉反馈，显示处理活跃状态

8. **完善的 Tooltip 系统**

   - 为所有按钮添加详细的功能说明
   - 内容包括：
     - 浏览按钮：说明选择的内容类型
     - 操作按钮：说明操作结果和快捷键
     - 危险按钮：明确警告不可撤销
   - 降低学习成本，提升易用性

**技术实现：**

1. **新增自定义组件** (`micro_tracker/components/custom_widgets.py`)

   - `RippleButton`：继承 QPushButton，实现波纹动画
   - `AnimatedProgressBar`：继承 QProgressBar，实现波浪动画
   - `FocusGlowLineEdit`：继承 QLineEdit，实现焦点发光
   - 使用 QPropertyAnimation 和 pyqtProperty 实现流畅动画
   - 保持与原组件相同的 API 接口，零侵入性替换

2. **样式系统重构** (`micro_tracker/config/style.py`)

   - 定义颜色常量：PRIMARY_COLOR、SECONDARY_COLOR、LIGHT_COLOR、DARK_COLOR
   - 统一圆角半径规范
   - 更新所有 QSS 样式表
   - 便于未来主题定制和维护

3. **组件逐个替换**
   - `setup_tab.py`：8 个按钮，4 个输入框，1 个进度条
   - `filter_tab.py`：5 个按钮，10 个输入框，1 个进度条
   - `result_preview_tab.py`：2 个按钮
   - `annotation_manager.py`：5 个按钮，1 个表格样式
   - `filter_conditions.py`：8 个输入框

**影响范围：**

- ✅ 全部 4 个标签页界面全面优化
- ✅ 所有交互元素增强反馈
- ✅ 视觉一致性显著提升
- ✅ 不影响任何业务逻辑和数据处理
- ✅ 完全向后兼容

**用户体验提升：**

- ✅ 视觉美观：专业的学术深蓝配色，统一的圆角设计
- ✅ 交互流畅：波纹动画和发光效果提供即时反馈
- ✅ 信息清晰：优化的间距和强调样式，层次分明
- ✅ 易于学习：完善的 tooltip 系统，降低学习成本
- ✅ 操作确信：动画和高亮状态减少误操作

**技术细节：**

**修改的核心文件**：

- `micro_tracker/config/style.py` - 颜色系统和样式规范
- `micro_tracker/components/custom_widgets.py` - 新增 3 个自定义组件
- `micro_tracker/ui/setup_tab.py` - 标注追踪标签页组件替换
- `micro_tracker/ui/filter_tab.py` - 筛选过滤标签页组件替换
- `micro_tracker/ui/result_preview_tab.py` - 结果预览标签页组件替换
- `micro_tracker/ui/annotation_manager.py` - 标注管理器组件替换
- `micro_tracker/ui/filter_conditions.py` - 筛选条件输入框替换
- `micro_tracker/ui/guide_tab.py` - 颜色更新

**新增组件类**：

- `RippleButton` - 42 行代码
- `AnimatedProgressBar` - 58 行代码
- `FocusGlowLineEdit` - 25 行代码

**性能考虑**：

- 动画使用硬件加速（QPropertyAnimation）
- 波纹效果仅在点击时触发，不影响日常性能
- 发光效果使用 QGraphicsEffect，GPU 加速
- 进度条动画仅在处理期间启用

---

### 🔄 向后兼容性

- ✅ 完全向后兼容
- ✅ 不影响数据格式和处理逻辑
- ✅ 纯 UI 视觉优化，无破坏性变更
- ✅ 自定义组件保持与原组件相同的 API

---

## [v2.5.1] - 2026-02-04

### 🐛 重要修复 (Critical Bug Fix)

#### 修复结果预览和筛选过滤画布允许标注操作的问题

**问题描述：**
用户可以在"结果预览"和"筛选过滤"标签页的视频画布上执行标注操作（绘制边界框、添加点击标注、删除对象等），但这些标签页的设计目的是只读查看处理结果，不应允许任何标注功能。

**问题根源：**

1. **类继承问题** (`micro_tracker/components/video_widgets.py`)

   - `ResultVideoLabel` 直接继承 `MultiLayerVideoView`
   - 完整继承了所有交互功能（边界框绘制、点击标注、对象选择、删除等）
   - 鼠标事件和键盘事件未被禁用

2. **影响范围：**
   - 结果预览标签页 (`result_label`)
   - 筛选过滤标签页 (`filter_video_label`)

**修复内容：**

1. **重写 `ResultVideoLabel` 事件处理方法**

   - **新增类文档说明**：明确说明该类用于只读显示，列出已启用和已禁用的功能
   - **添加只读标志位**：`self.read_only = True`
   - **清空覆盖层**：初始化时调用 `overlay_layer.clear_all()` 清除标注数据

   - **重写 `mousePressEvent()`**：

     - ✅ 保留：Ctrl+左键拖拽、中键重置缩放
     - ❌ 禁用：边界框绘制、点击标注、对象选择

   - **重写 `mouseMoveEvent()`**：

     - ✅ 保留：拖拽平移
     - ❌ 禁用：边界框绘制更新

   - **重写 `mouseReleaseEvent()`**：

     - ✅ 保留：拖拽结束处理
     - ❌ 禁用：边界框完成绘制

   - **重写 `keyPressEvent()`**：

     - ✅ 保留：Home 键重置缩放、空格/F/D 键视频控制
     - ❌ 禁用：Delete 删除、A 保存点击、Ctrl+S 保存并切换、Ctrl+C 清除点击、Ctrl+H 隐藏提示

   - **添加空方法**：`_handle_point_click()` 空实现防止意外调用

2. **保留的查看功能：**

   - 视频帧显示
   - Ctrl+滚轮缩放（100%-1000%）
   - Ctrl+左键拖拽平移
   - 中键或 Home 键重置缩放
   - 空格/F/D 键视频播放控制

3. **禁用的标注功能：**
   - 左键拖拽绘制边界框
   - 左键/右键点击添加正负向标注
   - 对象选择
   - Delete 键删除对象
   - A 键保存点击
   - Ctrl+S 保存并切换帧
   - Ctrl+C 清除临时点击
   - Ctrl+H 隐藏提示

**影响范围：**

- ✅ 修复了用户体验问题：结果预览和筛选过滤画布现在是真正的只读模式
- ✅ 不影响"参数设置与标注"标签页的 `VideoLabel`（标注功能仍正常）
- ✅ 不影响数据处理逻辑和输出格式
- ✅ 完全向后兼容

---

### 📊 技术细节

**修改的核心文件：**

- `micro_tracker/components/video_widgets.py` - 完全重写 `ResultVideoLabel` 类的事件处理

**修改的方法：**

- `ResultVideoLabel.__init__()` - 添加只读标志和清空覆盖层
- `ResultVideoLabel.mousePressEvent()` - 仅保留缩放平移
- `ResultVideoLabel.mouseMoveEvent()` - 仅保留拖拽平移
- `ResultVideoLabel.mouseReleaseEvent()` - 仅处理拖拽结束
- `ResultVideoLabel.keyPressEvent()` - 禁用标注快捷键
- `ResultVideoLabel._handle_point_click()` - 空实现

**新增文档：**

- `ResultVideoLabel` 类文档字符串，详细说明只读特性和启用/禁用的功能列表

---

### 🔄 向后兼容性

- ✅ 完全向后兼容
- ✅ 不影响标注数据和处理逻辑
- ✅ 纯 UI 交互改进，无破坏性变更

---

## [v2.5.0] - 2026-02-04

### ✨ 新增功能 (New Features)

#### 图像缩放与拖拽平移功能

**功能描述：**
为所有视频预览视图添加交互式缩放和拖拽平移功能，方便用户对图像细节进行精确检查和标注。

**核心功能：**

1. **鼠标滚轮缩放** (`micro_tracker/components/video_widgets.py`)

   - 快捷键：Ctrl + 鼠标滚轮
   - 缩放范围：100% ~ 1000% (1x ~ 10x)
   - 缩放中心：始终以鼠标位置为中心，无论图像大小和位置
   - 缩放步长：固定倍率 1.15x（约 15%）
   - 实时反馈：悬浮提示显示当前缩放百分比（2 秒后自动隐藏）
   - 边界提示：达到最小/最大缩放时显示视觉和文字提示

2. **拖拽平移功能**

   - 快捷键：Ctrl + 左键拖拽
   - 启用条件：图像放大后内容超出视图边界
   - 光标反馈：拖拽时光标变为手型
   - 功能隔离：拖拽期间自动禁用标注功能，释放后恢复
   - 流畅体验：手动实现像素级精确平移

3. **重置缩放功能**

   - 快捷键：鼠标中键点击 或 Home 键
   - 行为：重置到初始自适应状态（图像适应视图大小）
   - 自动居中：重新调整视图使图像居中显示

4. **独立视图控制**

   - 三个视频视图（视频标注、结果预览、筛选预览）各自独立缩放
   - 每个视图保持各自的缩放状态和位置
   - 切换视频时自动重置所有视图

5. **坐标精度保障**
   - 缩放和平移完全基于 Qt Graphics View 坐标系统
   - 标注和掩膜自动跟随图像变换，确保坐标准确
   - 标注线条固定像素宽度（Cosmetic pen），任意缩放下保持清晰可见

**技术实现：**

1. **手动锚点控制** (`wheelEvent()`)

   - 禁用 Qt 自动锚点机制（`setTransformationAnchor(NoAnchor)`）
   - 手动计算场景坐标偏移并调整滚动条
   - 确保任意缩放倍数下锚点精确

2. **手动拖拽实现** (`mousePressEvent()`, `mouseMoveEvent()`, `mouseReleaseEvent()`)

   - 跟踪鼠标移动距离（视图像素坐标）
   - 反向更新滚动条实现平移效果
   - 与标注事件完全隔离，无冲突

3. **UI 反馈优化**
   - 半透明悬浮提示显示缩放百分比
   - 达到边界时抖动动画（QPropertyAnimation + OutBounce 缓动）
   - 智能提示文本切换（"自适应" / "xxx%"）

**使用场景：**

- 精确检查微小目标物体的边界
- 高倍放大验证标注准确性
- 细致观察目标形变和特征
- 处理高分辨率显微图像

---

### 🔄 向后兼容性

- ✅ 完全向后兼容
- ✅ 不影响已保存的标注数据
- ✅ 不影响处理逻辑和输出格式
- ✅ 纯 UI 交互增强，无破坏性变更

---

### 📊 技术细节

**修改的核心文件：**

- `micro_tracker/components/video_widgets.py` - 缩放、拖拽、UI 反馈实现
- `micro_tracker/ui/main_window.py` - 新视频加载时重置缩放状态

**新增状态变量：**

- `manual_zoom_active` - 标记是否处于手动缩放状态
- `is_panning` - 标记是否处于拖拽状态
- `last_pan_pos` - 记录拖拽时的上一个鼠标位置
- `min_scale` / `max_scale` - 缩放范围限制（1.0 / 10.0）
- `zoom_step` - 缩放步长（1.15）

**新增方法：**

- `wheelEvent()` - 鼠标滚轮缩放处理
- `reset_zoom()` - 重置缩放状态
- `show_zoom_tip()` - 显示缩放提示
- `hide_zoom_tip()` - 隐藏缩放提示
- `show_zoom_boundary_feedback()` - 边界反馈动画
- `get_manual_zoom_state()` - 获取缩放状态（工具方法）

**用户体验提升：**

- ✅ 细节检查：高倍放大观察目标特征
- ✅ 精确标注：放大后标注更精准
- ✅ 流畅交互：无卡顿的缩放和平移体验
- ✅ 直观反馈：清晰的视觉和文字提示

---

## [v2.4.1] - 2026-01-28

### 🐛 重要修复 (Critical Bug Fixes)

#### 修复绘制第一个对象后自动切换到修正模式的问题

**问题描述：**
用户在新对象模式下绘制第一个边界框后，系统会意外地自动切换到修正模式，导致后续绘制新边界框时收到警告："⚠️ 修正模式下不能绘制新的边界框，请使用点击提示（符合 SAM2 官方规范）"。

**问题根源：**

1. `update_object_selector()` 方法在刷新对象下拉框时，`combo.clear()` 和 `combo.addItem()` 会自动触发 `currentIndexChanged` 信号
2. 该信号连接到 `on_object_selected()`，后者无条件地强制切换到修正模式
3. 即使用户处于新对象模式，系统也会在后台悄悄切换模式

**修复内容：**

1. **双重保护机制** (`micro_tracker/ui/setup_tab.py`)

   **保护层 1：阻塞信号**（第 647-672 行）

   - 在更新下拉框时使用 `combo.blockSignals(True)` 阻塞信号
   - 防止 `clear()` 和 `addItem()` 触发 `currentIndexChanged`
   - 更新完成后恢复信号
   - 只在修正模式下才自动选中第一个对象

   **保护层 2：模式检查**（第 690-693 行）

   - 在 `on_object_selected()` 中添加模式检查
   - 只有在修正模式下才设置修正模式
   - 避免在新对象模式下被意外触发

2. **修复效果**：
   - ✅ 新对象模式下绘制第一个边界框后，保持在新对象模式
   - ✅ 可以连续绘制多个新对象（Obj_0, Obj_1, Obj_2...）
   - ✅ 手动切换到修正模式时，正确选中对象并应用修正模式
   - ✅ 删除对象时，仅更新下拉框，不改变当前模式

---

#### 修复对象删除机制 - 现支持删除所有帧的标注

**问题描述：**
之前的删除机制只删除当前帧的标注，如果对象在多个帧有标注（如第 0 帧、第 5 帧、第 10 帧），用户需要逐个切换到每一帧并删除，非常繁琐。

**用户期望：**
按一次 Delete 键应该完全删除对象及其在所有帧的标注。

**修复内容：**

1. **完全重写 `delete_selected_bbox()` 方法** (`micro_tracker/components/video_widgets.py` 第 797-869 行)

   **新行为：**

   - 删除该对象在**所有帧**的边界框标注
   - 删除该对象在**所有帧**的点击标注
   - 清除临时点击（如果正在编辑该对象）
   - 完全移除对象注册信息和固定颜色
   - 清理轨迹、特征数据
   - 清理预览 masks
   - 自动同步当前帧显示

2. **更新日志信息** (`micro_tracker/ui/main_window.py`)

   - 修改删除提示信息，明确说明删除范围
   - 新提示："已删除对象 X 在所有帧的标注（包括边界框和点击标注）"

3. **两种删除方式对比**：

   | 删除方式       | 触发方式               | 删除范围                 | 用途                 |
   | -------------- | ---------------------- | ------------------------ | -------------------- |
   | **删除对象**   | 选中边界框 + Delete 键 | 该对象在**所有帧**的标注 | 完全移除某个对象     |
   | **删除帧标注** | 标注管理器的"删除"按钮 | **指定帧**的所有对象标注 | 移除某一帧的所有标注 |

4. **使用场景示例**：
   - 对象 0 在第 0 帧、第 5 帧、第 10 帧有标注
   - 对象 1 在第 0 帧、第 8 帧有标注
   - 在任意帧选中对象 0 后按 Delete
   - 结果：对象 0 在所有帧（0、5、10）的标注全部删除
   - 对象 1 的标注不受影响

---

### 🔄 向后兼容性

- ✅ 完全向后兼容
- ✅ 不影响已保存的标注 JSON 文件
- ✅ 不影响处理逻辑和输出格式

---

### 📊 技术细节

**修改的核心文件：**

- `micro_tracker/ui/setup_tab.py` - 修复模式自动切换问题（双重保护）
- `micro_tracker/components/video_widgets.py` - 重写对象删除机制
- `micro_tracker/ui/main_window.py` - 更新删除日志信息

**测试建议：**

1. 测试新对象模式下连续绘制多个对象
2. 测试修正模式的正常切换和对象选择
3. 测试删除对象是否正确清除所有帧的标注
4. 测试标注管理器的列表更新和刷新

---

## [v2.4.0] - 2026-01-20

### ✨ 新增功能 (New Features)

#### 标注自动保存功能

**功能描述：**
在点击"开始处理"按钮时，系统会自动将标注数据保存到 Results 文件夹，无需手动导出，确保数据安全。

**核心功能：**

1. **自动保存时机** (`micro_tracker/controllers/processing_controller.py`)

   - 在开始视频处理之前自动触发保存
   - 保存路径自动生成：`Results_{输入名}/{输入名}_annotations.json`
   - 如果文件已存在，会提示用户是否覆盖

2. **保存内容包括**：

   - 完整的边界框信息
   - 点击提示数据
   - 对象注册表
   - 标注模式和版本信息

3. **用户友好的提示**：
   - 保存成功时显示成功消息
   - 文件存在时询问是否覆盖
   - 用户可选择取消处理操作

**使用场景：**

- 避免标注数据丢失
- 确保每次处理都有对应的标注记录
- 便于后续分析和重现处理流程

---

### 🎨 UI/UX 改进 (UI/UX Improvements)

#### 标注管理器界面优化

**改进内容：**

1. **布局重新设计** (`micro_tracker/ui/annotation_manager.py`)

   - 将按钮区从底部改为右侧垂直布局
   - 按钮更大更易点击（最小宽度 80px，最小高度 35px）
   - 表格占据更多空间，显示更多标注信息
   - 移除最大高度限制，表格可以自由伸展

2. **按钮功能优化**：

   - 移除"导出"按钮（已改为自动保存）
   - 移除"刷新"按钮（改为自动刷新）
   - 保留"导入标注"、"清空所有"、"标注说明"三个核心按钮
   - 按钮顺序更符合使用逻辑

3. **自动刷新机制**：

   - 标注操作后自动刷新列表（添加对象、删除对象、保存点击）
   - 无需手动点击刷新按钮
   - 提升用户体验流畅度

4. **帮助文档更新**：
   - 更新标注说明，明确自动保存机制
   - 移除手动导出相关说明
   - 添加自动保存相关 FAQ

#### 用户反馈增强

**改进内容：**

1. **欢迎消息优化** (`micro_tracker/ui/setup_tab.py`)

   - 明确指定支持的视频格式：MP4、AVI、MOV、MKV
   - 提供更清晰的使用指引

2. **筛选日志增强** (`micro_tracker/controllers/filter_controller.py`)

   - 在筛选日志中显示对象的实际面积（μm²）
   - 显示对象的实际位移（μm）
   - 提供更详细的筛选原因说明
   - 便于用户理解筛选结果

3. **界面文字优化**：
   - 简化过滤器信息标签，移除冗余文字
   - 提高文字可读性和界面清晰度

---

### 🐛 修复 (Bug Fixes)

#### 修复对象 ID 类型一致性问题

**问题描述：**
在某些情况下，对象 ID 可能以字符串类型存在，导致后续处理时类型不匹配错误。

**修复内容：**

1. **强制类型转换** (`micro_tracker/components/video_widgets.py`)

   - 在设置标注模式时确保 `obj_id` 为整数类型
   - 在删除边界框时确保返回的 `obj_id` 为整数
   - 在添加点击提示时确保 `obj_id` 为整数

2. **导入数据验证** (`micro_tracker/ui/annotation_manager.py`)
   - 从 JSON 导入时强制转换对象 ID 为整数
   - 确保数据一致性

**影响范围：**

- 修复了对象 ID 类型不一致导致的潜在 bug
- 提升了系统稳定性

---

### 🔄 向后兼容性

- ✅ 完全向后兼容
- ✅ 旧版本的标注 JSON 文件可以正常导入
- ✅ 不影响现有的处理逻辑和输出格式
- ✅ UI 改进不影响核心功能

---

### 📊 技术细节

**修改的核心文件：**

- `micro_tracker/controllers/processing_controller.py` - 自动保存逻辑
- `micro_tracker/ui/annotation_manager.py` - UI 布局和自动刷新
- `micro_tracker/components/video_widgets.py` - ID 类型一致性
- `micro_tracker/ui/main_window.py` - 标签页名称和刷新逻辑
- `micro_tracker/ui/setup_tab.py` - 欢迎消息和界面文字

**用户体验提升：**

- ✅ 数据安全：自动保存防止数据丢失
- ✅ 操作简化：移除手动导出步骤
- ✅ 界面优化：更大的按钮、更好的布局
- ✅ 反馈增强：更详细的日志和提示信息

---

## [v2.3.1] - 2026-01-19

### 📝 文档维护 (Documentation Maintenance)

**版本说明：**
本版本为常规维护版本，更新项目文档中的版本号和日期信息。

**更新内容：**

1. **更新 README.md**

   - 更新版本徽章至 v2.3.1

2. **更新 CHANGELOG.md**

   - 添加 v2.3.1 版本条目

3. **更新使用指南 (guide_tab.py)**
   - 更新版本信息至 v2.3.1
   - 更新发布日期至 2026 年 1 月 19 日

### 🔄 向后兼容性

- ✅ 完全向后兼容，无代码变更
- ✅ 不影响任何功能和数据格式
- ✅ 纯文档性质更新

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
   - 更新发布日期至 2026 年 1 月 5 日
   - 更新版权信息至 2026 年

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
