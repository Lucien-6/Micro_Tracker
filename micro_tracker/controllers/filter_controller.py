import os
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDateTime
import cv2
import numpy as np
import pandas as pd
from pathlib import Path

class FilterController:
    """筛选控制器，负责管理筛选过滤相关功能"""
    
    def __init__(self, main_window):
        """
        初始化筛选控制器
        
        Args:
            main_window: 主窗口引用
        """
        self.main_window = main_window
    
    def apply_mask_filter(self):
        """应用掩膜筛选"""
        # 获取掩膜目录
        mask_dir = self.main_window.filter_mask_dir_edit.text()
        if not mask_dir or not os.path.exists(mask_dir):
            self.main_window.log_message("错误: 请先选择有效的掩膜文件夹", "error")
            return
        
        # 获取参数
        try:
            fps = float(self.main_window.fps_input.text())
            um_per_pixel = float(self.main_window.um_per_pixel_input.text())
        except ValueError:
            self.main_window.log_message("错误: 帧率和像素比例必须为有效数字", "error")
            return
        
        # 解析排除ID列表
        exclude_ids = []
        if self.main_window.exclude_ids_input.text().strip():
            try:
                exclude_ids = [int(x.strip()) for x in self.main_window.exclude_ids_input.text().split(',')]
            except ValueError:
                self.main_window.log_message("错误: 排除ID必须为整数，多个ID用逗号分隔", "error")
                return
        
        # 构建筛选参数
        filter_params = {
            'exclude_ids': exclude_ids
        }
        
        # 面积区间
        if self.main_window.area_filter_check.isChecked():
            try:
                area_min = float(self.main_window.area_min_input.text())
                area_max = float(self.main_window.area_max_input.text())
                filter_params['area_filter'] = True
                filter_params['area_min'] = area_min
                filter_params['area_max'] = area_max
            except ValueError:
                self.main_window.log_message("错误: 面积区间必须为有效数字", "error")
                return
        
        # 面积变化率
        if self.main_window.area_change_check.isChecked():
            try:
                area_change_threshold = float(self.main_window.area_change_input.text())
                if not 0 <= area_change_threshold <= 1:
                    raise ValueError("面积变化率必须在0到1之间")
                filter_params['area_change_filter'] = True
                filter_params['area_change_threshold'] = area_change_threshold
            except ValueError as e:
                self.main_window.log_message(f"错误: {str(e)}", "error")
                return
        
        # 瞬时速度区间
        if self.main_window.velocity_check.isChecked():
            try:
                velocity_min = float(self.main_window.velocity_min_input.text())
                velocity_max = float(self.main_window.velocity_max_input.text())
                filter_params['velocity_filter'] = True
                filter_params['velocity_min'] = velocity_min
                filter_params['velocity_max'] = velocity_max
            except ValueError:
                self.main_window.log_message("错误: 速度区间必须为有效数字", "error")
                return
        
        # 总位移区间
        if self.main_window.displacement_check.isChecked():
            try:
                displacement_min = float(self.main_window.displacement_min_input.text())
                displacement_max = float(self.main_window.displacement_max_input.text())
                filter_params['displacement_filter'] = True
                filter_params['displacement_min'] = displacement_min
                filter_params['displacement_max'] = displacement_max
            except ValueError:
                self.main_window.log_message("错误: 位移区间必须为有效数字", "error")
                return
        
        # 边界截断排除
        filter_params['boundary_filter'] = self.main_window.boundary_check.isChecked()
        
        # 相互最短距离
        if self.main_window.min_distance_check.isChecked():
            try:
                min_distance_threshold = float(self.main_window.min_distance_input.text())
                filter_params['min_distance_filter'] = True
                filter_params['min_distance_threshold'] = min_distance_threshold
            except ValueError:
                self.main_window.log_message("错误: 距离阈值必须为有效数字", "error")
                return
        
        # 清空筛选日志区域
        self.main_window.filter_log_text.clear()
        
        # 记录筛选参数到日志
        self.filter_log_message("====== 开始筛选掩膜数据 ======", "highlight")
        self.filter_log_message(f"掩膜文件夹: {mask_dir}", "info")
        self.filter_log_message(f"帧率: {fps} FPS", "info")
        self.filter_log_message(f"像素比例: {um_per_pixel} μm/pixel", "info")
        
        # 记录启用的筛选条件
        active_filters = []
        if filter_params.get('area_filter', False):
            active_filters.append(f"面积区间: {filter_params['area_min']} - {filter_params['area_max']} μm²")
        if filter_params.get('area_change_filter', False):
            active_filters.append(f"面积变化率阈值: {filter_params['area_change_threshold']}")
        if filter_params.get('velocity_filter', False):
            active_filters.append(f"瞬时速度区间: {filter_params['velocity_min']} - {filter_params['velocity_max']} μm/s")
        if filter_params.get('displacement_filter', False):
            active_filters.append(f"总位移区间: {filter_params['displacement_min']} - {filter_params['displacement_max']} μm")
        if filter_params.get('boundary_filter', False):
            active_filters.append("边界截断排除")
        if filter_params.get('min_distance_filter', False):
            active_filters.append(f"相互最短距离阈值: {filter_params['min_distance_threshold']} μm")
        if filter_params.get('exclude_ids', []):
            active_filters.append(f"排除指定ID: {', '.join(map(str, filter_params['exclude_ids']))}")
        
        if active_filters:
            self.filter_log_message("启用的筛选条件:", "highlight")
            for f in active_filters:
                self.filter_log_message(f"- {f}", "info")
        else:
            self.filter_log_message("未启用任何筛选条件，将保留所有对象", "warning")
        
        # 创建并启动筛选线程
        self.main_window.filter_thread = self.main_window.FilterMaskThread(mask_dir, fps, um_per_pixel, filter_params)
        self.main_window.filter_thread.progress_update.connect(self.update_filter_progress)
        self.main_window.filter_thread.progress_percent.connect(self.update_filter_progress_bar)
        self.main_window.filter_thread.filter_finished.connect(self.filter_processing_done)
        self.main_window.filter_thread.frame_processed.connect(self.update_filter_frame)
        self.main_window.filter_thread.stats_update.connect(self.update_filter_stats)
        
        # 显示进度条
        self.main_window.filter_progress_bar.setValue(0)
        self.main_window.filter_progress_bar.setVisible(True)
        
        # 禁用筛选按钮
        self.main_window.apply_filter_btn.setEnabled(False)
        
        # 开始筛选
        self.main_window.filter_thread.start()
    
    def update_filter_progress(self, message):
        """更新筛选处理进度信息"""
        # 根据消息内容确定类型
        msg_type = "info"
        if "错误" in message:
            msg_type = "error"
        elif "警告" in message:
            msg_type = "warning"
        elif "成功" in message or "完成" in message:
            msg_type = "success"
        elif "进度" in message or "剩余时间" in message or "帧" in message:
            msg_type = "progress"
        
        # 在筛选日志区域显示消息
        self.filter_log_message(message, msg_type)
    
    def filter_log_message(self, message, msg_type="info"):
        """在筛选过滤日志区域添加消息，并根据消息类型设置样式"""
        color_map = {
            "info": "#424242",     # 黑色 - 一般信息
            "success": "#2E7D32",  # 绿色 - 成功消息
            "warning": "#FF8F00",  # 橙色 - 警告消息
            "error": "#C62828",    # 红色 - 错误消息
            "highlight": "#1565C0", # 蓝色 - 高亮信息
            "progress": "#6A1B9A"  # 紫色 - 进度信息
        }
        
        # 设置文本颜色
        color = color_map.get(msg_type, "#424242")
        
        # 直接设置带颜色的消息文本，不添加时间前缀
        formatted_message = f"<span style='color: {color};'>{message}</span>"
        
        # 添加到文本框
        self.main_window.filter_log_text.append(formatted_message)
        
        # 滚动到底部
        self.main_window.filter_log_text.verticalScrollBar().setValue(
            self.main_window.filter_log_text.verticalScrollBar().maximum()
        )
        
        # 如果有错误或警告，也记录到主日志中
        if msg_type in ["error", "warning"]:
            self.main_window.log_message(message, msg_type)
        
        # 更新UI
        QApplication.processEvents()
    
    def update_filter_progress_bar(self, percent):
        """更新筛选进度条"""
        self.main_window.filter_progress_bar.setValue(percent)
        QApplication.processEvents()
    
    def update_filter_stats(self, total_objects, passed_objects):
        """更新筛选统计信息"""
        self.main_window.filter_stats_label.setText(f"对象数量: {total_objects} | 通过筛选: {passed_objects}")
    
    def update_filter_frame(self, frame, current_idx, total_frames):
        """更新筛选结果预览帧"""
        if frame is None:
            return
        
        # 更新筛选预览标签
        self.main_window.filter_video_label.setVideoFrame(frame)
        
        # 更新滑块
        if self.main_window.filter_slider.maximum() != total_frames - 1:
            self.main_window.filter_slider.setRange(0, total_frames - 1)
        self.main_window.filter_slider.setValue(current_idx)
        self.main_window.filter_slider.setEnabled(True)
        
        # 更新信息标签
        percent = int((current_idx + 1) / total_frames * 100)
        self.main_window.filter_info_label.setText(f"筛选结果: {current_idx+1}/{total_frames} ({percent}%)")
    
    def filter_processing_done(self, success, message):
        """筛选处理完成回调"""
        # 隐藏进度条
        self.main_window.filter_progress_bar.setVisible(False)
        
        # 更新日志
        if success:
            self.filter_log_message("====== 筛选完成 ======", "highlight")
            self.filter_log_message(message, "success")
            
            # 汇报各对象的筛选截断情况及具体原因
            if hasattr(self.main_window.filter_thread, 'object_filter_results') and self.main_window.filter_thread.object_filter_results:
                # 分组统计各类结果
                result_counts = {'passed': 0, 'truncated': 0, 'filtered': 0}
                for obj_id, result in self.main_window.filter_thread.object_filter_results.items():
                    if result['result'] in result_counts:
                        result_counts[result['result']] += 1
                
                self.filter_log_message("", "info")  # 添加空行
                self.filter_log_message("===== 对象筛选结果汇总 =====", "highlight")
                self.filter_log_message(f"总对象数: {self.main_window.filter_thread.total_objects}", "info")
                # 修改通过筛选的对象数量，包括完全通过的对象和部分截断的对象
                passed_total = result_counts['passed'] + result_counts['truncated']
                self.filter_log_message(f"通过筛选: {passed_total} 个对象 (完全通过: {result_counts['passed']}, 部分截断: {result_counts['truncated']})", "success")
                self.filter_log_message(f"完全过滤: {result_counts['filtered']} 个对象", "error")
                self.filter_log_message("", "info")  # 添加空行
                
                # 按对象ID排序
                sorted_obj_ids = sorted(self.main_window.filter_thread.object_filter_results.keys())
                
                # 显示通过筛选的对象
                if result_counts['passed'] > 0:
                    self.filter_log_message("【完全通过筛选的对象】", "success")
                    for obj_id in sorted_obj_ids:
                        result = self.main_window.filter_thread.object_filter_results[obj_id]
                        if result['result'] == 'passed':
                            frames_info = f"{result['frames']}/{result['original_frames']} 帧"
                            self.filter_log_message(f"对象 {obj_id}: {frames_info} - {result['reason']}", "success")
                    self.filter_log_message("", "info")  # 添加空行
                
                # 显示部分截断的对象
                if result_counts['truncated'] > 0:
                    self.filter_log_message("【部分截断的对象】", "warning")
                    for obj_id in sorted_obj_ids:
                        result = self.main_window.filter_thread.object_filter_results[obj_id]
                        if result['result'] == 'truncated':
                            truncated_at = result.get('truncated_at', 0)
                            original_frames = result.get('original_frames', 0)
                            valid_frames = truncated_at + 1
                            frames_percent = int((valid_frames / original_frames) * 100) if original_frames > 0 else 0
                            frames_info = f"保留 {valid_frames}/{original_frames} 帧 ({frames_percent}%)"
                            self.filter_log_message(f"对象 {obj_id}: {frames_info} - {result['reason']}", "warning")
                    self.filter_log_message("", "info")  # 添加空行
                
                # 显示完全过滤的对象
                if result_counts['filtered'] > 0:
                    self.filter_log_message("【完全过滤的对象】", "error")
                    for obj_id in sorted_obj_ids:
                        result = self.main_window.filter_thread.object_filter_results[obj_id]
                        if result['result'] == 'filtered':
                            self.filter_log_message(f"对象 {obj_id}: {result['reason']}", "error")
                    self.filter_log_message("", "info")  # 添加空行
            
            # 启用播放按钮和保存按钮
            self.main_window.filter_play_pause_btn.setEnabled(True)
            self.main_window.save_filter_btn.setEnabled(True)
            
            # 初始化筛选视频播放线程
            self.start_filter_video_playback()
            
            # 重新启用筛选按钮，使用户可以修改参数后再次执行
            self.main_window.apply_filter_btn.setEnabled(True)
        else:
            self.filter_log_message("====== 筛选失败 ======", "highlight")
            self.filter_log_message(f"筛选失败: {message}", "error")
            
            # 重新启用筛选按钮
            self.main_window.apply_filter_btn.setEnabled(True)
    
    def start_filter_video_playback(self):
        """初始化并开始筛选结果视频播放"""
        if not hasattr(self.main_window, 'filter_thread') or not self.main_window.filter_thread.filtered_masks:
            return
        
        # 停止之前的视频线程
        if hasattr(self.main_window, 'filter_video_thread') and self.main_window.filter_video_thread.isRunning():
            self.main_window.filter_video_thread.stop()
        
        # 创建新的视频线程
        self.main_window.filter_video_thread = self.main_window.FilterVideoThread(self.main_window.filter_thread.filtered_masks)
        self.main_window.filter_video_thread.frame_ready.connect(self.main_window.filter_video_label.setVideoFrame)
        self.main_window.filter_video_thread.frame_index_changed.connect(self.update_filter_slider)
        
        # 设置帧率
        try:
            fps = float(self.main_window.fps_input.text())
            # 限制预览帧率在合理范围
            preview_fps = min(max(fps, 1), 30)
            self.main_window.filter_video_thread.set_fps(preview_fps)
        except:
            pass
        
        # 开始线程
        self.main_window.filter_video_thread.start()
        
        # 更新播放按钮状态
        self.main_window.filter_play_pause_btn.setText("播放")
        self.main_window.filter_play_pause_btn.setIcon(QIcon.fromTheme("media-playback-start"))
    
    def update_filter_slider(self, frame_index):
        """更新筛选预览滑块位置"""
        # 暂时断开滑块的valueChanged信号连接，避免循环触发
        self.main_window.filter_slider.blockSignals(True)
        self.main_window.filter_slider.setValue(frame_index)
        self.main_window.filter_slider.blockSignals(False)
        
        # 更新帧信息标签
        total_frames = len(self.main_window.filter_thread.filtered_masks) if hasattr(self.main_window, 'filter_thread') else 0
        percent = int((frame_index + 1) / total_frames * 100) if total_frames > 0 else 0
        self.main_window.filter_info_label.setText(f"筛选结果: {frame_index+1}/{total_frames} ({percent}%)")
    
    def save_filter_results(self):
        """保存筛选结果"""
        if not hasattr(self.main_window, 'filter_thread') or not self.main_window.filter_thread.object_trajectories:
            self.filter_log_message("错误: 没有可保存的筛选结果", "error")
            return
        
        # 显示进度条
        self.main_window.filter_progress_bar.setValue(0)
        self.main_window.filter_progress_bar.setVisible(True)
        
        try:
            # 禁用保存按钮，避免重复操作
            self.main_window.save_filter_btn.setEnabled(False)
            
            # 1. 创建保存文件夹
            self.filter_log_message("====== 开始保存筛选结果 ======", "highlight")
            mask_dir = self.main_window.filter_mask_dir_edit.text()
            base_dir = os.path.dirname(mask_dir)
            
            # 获取原始视频文件名（不含扩展名）
            video_name = "video"
            
            # 优先从主窗口的video_path获取
            if hasattr(self.main_window, 'video_path') and self.main_window.video_path:
                video_filename = os.path.basename(self.main_window.video_path)
                video_name = os.path.splitext(video_filename)[0]
            # 如果没有直接的视频路径，尝试从掩膜文件夹名称推断
            else:
                # 掩膜目录通常命名为 "masks_视频名"
                mask_dirname = os.path.basename(mask_dir)
                if mask_dirname.startswith("masks_"):
                    video_name = mask_dirname[6:]  # 去掉 "masks_" 前缀
            
            self.filter_log_message(f"使用原始视频名称: {video_name}", "info")
            
            # 创建Filtered_Masks文件夹，使用原始视频名称
            filtered_masks_dir = os.path.join(base_dir, f"Filtered_Masks_{video_name}")
            os.makedirs(filtered_masks_dir, exist_ok=True)
            self.filter_log_message(f"已创建筛选掩膜保存目录: {filtered_masks_dir}", "info")
            
            # 2. 保存筛选后的掩膜图片
            self.filter_log_message("正在保存筛选后的掩膜图片...", "progress")
            
            # 获取原始掩膜尺寸
            h, w = self.main_window.filter_thread.original_masks[0].shape if self.main_window.filter_thread.original_masks else (0, 0)
            
            # 创建新的掩膜图像保存筛选后的对象
            total_frames = len(self.main_window.filter_thread.original_masks)
            object_ids = list(self.main_window.filter_thread.object_trajectories.keys())
            self.filter_log_message(f"需要处理 {total_frames} 帧, 包含 {len(object_ids)} 个通过筛选的对象", "info")
            
            # 对每一帧保存筛选后的掩膜
            for frame_idx in range(total_frames):
                # 更新进度条, 掩膜保存占总进度的60%
                percent = int((frame_idx / total_frames) * 60)
                self.update_filter_progress_bar(percent)
                
                # 创建空白掩膜
                filtered_mask = np.zeros((h, w), dtype=np.uint8)
                
                # 查找当前帧中通过筛选的对象
                objects_in_frame = 0
                for obj_id in object_ids:
                    # 检查该对象是否在当前帧有数据
                    obj_in_frame = False
                    obj_data = self.main_window.filter_thread.object_trajectories[obj_id]
                    
                    for data_point in obj_data:
                        time_sec = data_point['time']
                        frame_time = frame_idx / float(self.main_window.fps_input.text())
                        
                        # 允许一定的误差
                        if abs(time_sec - frame_time) < 0.001:
                            obj_in_frame = True
                            objects_in_frame += 1
                            break
                    
                    if obj_in_frame:
                        # 从原始掩膜提取此对象
                        original_mask = self.main_window.filter_thread.original_masks[frame_idx]
                        obj_pixels = (original_mask == obj_id)
                        
                        # 将对象添加到新掩膜
                        filtered_mask[obj_pixels] = obj_id
                
                # 保存结果掩膜
                output_path = os.path.join(filtered_masks_dir, f"frame_{frame_idx:04d}.png")
                cv2.imwrite(output_path, filtered_mask)
                
                # 每保存5个掩膜更新一次进度
                if frame_idx % 5 == 0 or frame_idx == total_frames - 1:
                    percent_complete = int((frame_idx + 1) / total_frames * 100)
                    self.filter_log_message(f"掩膜保存进度: {frame_idx+1}/{total_frames} ({percent_complete}%) - 当前帧包含 {objects_in_frame} 个对象", "progress")
            
            # 3. 保存轨迹数据到Excel
            self.filter_log_message("", "info")  # 添加空行
            self.filter_log_message("正在保存轨迹数据到Excel...", "progress")
            self.update_filter_progress_bar(65)
            
            try:
                import pandas as pd
                
                # 创建Excel文件，使用原始视频名称
                excel_path = os.path.join(base_dir, f"Trajectories_Results_{video_name}.xlsx")
                
                # 统计数据点总数
                total_data_points = sum(len(trajectory) for trajectory in self.main_window.filter_thread.object_trajectories.values())
                self.filter_log_message(f"正在处理 {len(object_ids)} 个对象的轨迹, 共 {total_data_points} 个数据点", "info")
                
                # 创建ExcelWriter
                with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                    # 首先创建参数信息sheet
                    self.filter_log_message("创建参数信息表...", "info")
                    
                    # 收集筛选参数
                    parameters_data = {
                        "Parameter": [
                            "Video Path",
                            "Mask Directory",
                            "FPS",
                            "Pixel Scale (μm/pixel)",
                            "Exclude Object IDs",
                            "Area Filter",
                            "Area Range (μm²)",
                            "Area Change Filter",
                            "Area Change Threshold",
                            "Velocity Filter",
                            "Velocity Range (μm/s)",
                            "Displacement Filter",
                            "Displacement Range (μm)",
                            "Boundary Truncation",
                            "Minimum Distance Filter",
                            "Minimum Distance Threshold (μm)",
                            "Total Objects",
                            "Passed Objects",
                            "Filtered Objects"
                        ],
                        "Value": [
                            self.main_window.video_path if hasattr(self.main_window, 'video_path') else "Unknown",
                            mask_dir,
                            self.main_window.fps_input.text(),
                            self.main_window.um_per_pixel_input.text(),
                            ", ".join(map(str, self.main_window.filter_thread.filter_params.get('exclude_ids', []))) if self.main_window.filter_thread.filter_params.get('exclude_ids') else "None",
                            "Enabled" if self.main_window.filter_thread.filter_params.get('area_filter', False) else "Disabled",
                            f"{self.main_window.filter_thread.filter_params.get('area_min', 0)} - {self.main_window.filter_thread.filter_params.get('area_max', 'inf')}" if self.main_window.filter_thread.filter_params.get('area_filter', False) else "N/A",
                            "Enabled" if self.main_window.filter_thread.filter_params.get('area_change_filter', False) else "Disabled",
                            str(self.main_window.filter_thread.filter_params.get('area_change_threshold', 'N/A')) if self.main_window.filter_thread.filter_params.get('area_change_filter', False) else "N/A",
                            "Enabled" if self.main_window.filter_thread.filter_params.get('velocity_filter', False) else "Disabled",
                            f"{self.main_window.filter_thread.filter_params.get('velocity_min', 0)} - {self.main_window.filter_thread.filter_params.get('velocity_max', 'inf')}" if self.main_window.filter_thread.filter_params.get('velocity_filter', False) else "N/A",
                            "Enabled" if self.main_window.filter_thread.filter_params.get('displacement_filter', False) else "Disabled",
                            f"{self.main_window.filter_thread.filter_params.get('displacement_min', 0)} - {self.main_window.filter_thread.filter_params.get('displacement_max', 'inf')}" if self.main_window.filter_thread.filter_params.get('displacement_filter', False) else "N/A",
                            "Enabled" if self.main_window.filter_thread.filter_params.get('boundary_filter', False) else "Disabled",
                            "Enabled" if self.main_window.filter_thread.filter_params.get('min_distance_filter', False) else "Disabled",
                            str(self.main_window.filter_thread.filter_params.get('min_distance_threshold', 'N/A')) if self.main_window.filter_thread.filter_params.get('min_distance_filter', False) else "N/A",
                            str(self.main_window.filter_thread.total_objects),
                            str(self.main_window.filter_thread.passed_objects),
                            str(self.main_window.filter_thread.total_objects - self.main_window.filter_thread.passed_objects)
                        ]
                    }
                    
                    # 创建参数DataFrame
                    params_df = pd.DataFrame(parameters_data)
                    
                    # 写入参数sheet
                    params_df.to_excel(writer, sheet_name="Parameters", index=False)
                    
                    # 自适应列宽
                    worksheet = writer.sheets["Parameters"]
                    for i, col in enumerate(params_df.columns):
                        max_width = max(
                            params_df[col].astype(str).map(len).max(),
                            len(col)
                        ) + 2  # 添加一些额外空间
                        worksheet.column_dimensions[chr(65 + i)].width = max_width
                    
                    # 然后保存对象轨迹sheets
                    obj_count = 0
                    for obj_id, trajectory in self.main_window.filter_thread.object_trajectories.items():
                        obj_count += 1
                        # 更新进度条, Excel保存占总进度的20%
                        excel_percent = 65 + int((obj_count / len(object_ids)) * 20)
                        self.update_filter_progress_bar(excel_percent)
                        
                        # 转换为DataFrame
                        df = pd.DataFrame(trajectory)
                        
                        # 仅保留micro_tracker.py中指定的列
                        df = df[['time', 'area', 'center_x', 'center_y', 'major_axis', 'minor_axis', 'angle']]
                        
                        # 列名重命名与micro_tracker.py完全一致
                        df = df.rename(columns={
                            'time': 'time (s)',
                            'area': 'area (μm²)',
                            'center_x': 'center_x (μm)',
                            'center_y': 'center_y (μm)',
                            'major_axis': 'major axis length (μm)',
                            'minor_axis': 'minor axis length (μm)',
                            'angle': 'posture angle (°)'
                        })
                        
                        # 保存到Excel的sheet
                        sheet_name = f"Object_{obj_id}"
                        df.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        # 自适应列宽
                        worksheet = writer.sheets[sheet_name]
                        for i, col in enumerate(df.columns):
                            max_width = max(
                                df[col].astype(str).map(len).max(),
                                len(col)
                            ) + 2  # 添加一些额外空间
                            worksheet.column_dimensions[chr(65 + i)].width = max_width
                        
                        # 定期更新进度
                        if obj_count % 5 == 0 or obj_count == len(object_ids):
                            percent_complete = int((obj_count / len(object_ids)) * 100)
                            self.filter_log_message(f"Excel数据保存进度: {obj_count}/{len(object_ids)} 个对象 ({percent_complete}%)", "progress")
                
                self.filter_log_message(f"轨迹数据已保存到Excel文件: {excel_path}", "success")
                self.update_filter_progress_bar(90)  # 90%进度
                
            except ImportError:
                # 如果没有pandas，使用CSV格式保存
                self.filter_log_message("警告: 未安装pandas库，将使用CSV格式保存轨迹数据", "warning")
                
                # 为每个对象创建CSV文件
                obj_count = 0
                csv_files = []
                
                for obj_id, trajectory in self.main_window.filter_thread.object_trajectories.items():
                    obj_count += 1
                    # 更新进度条, CSV保存占总进度的20%
                    csv_percent = 65 + int((obj_count / len(object_ids)) * 20)
                    self.update_filter_progress_bar(csv_percent)
                    
                    csv_path = os.path.join(base_dir, f"Object_{obj_id}_Trajectory_{video_name}.csv")
                    csv_files.append(csv_path)
                    
                    with open(csv_path, 'w', newline='') as csvfile:
                        # 写入标题行，与micro_tracker.py一致
                        header = "time (s),area (μm²),center_x (μm),center_y (μm),major axis length (μm),minor axis length (μm),posture angle (°)\n"
                        csvfile.write(header)
                        
                        # 写入数据行
                        for point in trajectory:
                            line = f"{point['time']},{point['area']},{point['center_x']},{point['center_y']},{point['major_axis']},{point['minor_axis']},{point['angle']}\n"
                            csvfile.write(line)
                    
                    # 定期更新进度
                    if obj_count % 5 == 0 or obj_count == len(object_ids):
                        percent_complete = int((obj_count / len(object_ids)) * 100)
                        self.filter_log_message(f"CSV数据保存进度: {obj_count}/{len(object_ids)} 个对象 ({percent_complete}%)", "progress")
                
                # 列出所有生成的CSV文件
                csv_dir = os.path.dirname(csv_files[0])
                self.filter_log_message(f"轨迹数据已保存到CSV文件夹: {csv_dir}", "success")
                self.update_filter_progress_bar(90)  # 90%进度
            
            # 完成保存
            self.update_filter_progress_bar(100)  # 100%进度
            self.filter_log_message("", "info")  # 添加空行
            self.filter_log_message("====== 保存完成 ======", "highlight")
            self.filter_log_message(f"筛选掩膜已保存到: {filtered_masks_dir}", "success")
            
            # 统计和总结信息
            self.filter_log_message("", "info")  # 添加空行
            self.filter_log_message("【保存结果统计】", "highlight")
            self.filter_log_message(f"- 总帧数: {total_frames} 帧", "info")
            self.filter_log_message(f"- 对象数: {len(object_ids)} 个", "info")
            frames_per_obj = {}
            for obj_id, trajectory in self.main_window.filter_thread.object_trajectories.items():
                frames_per_obj[obj_id] = len(trajectory)
            avg_frames = sum(frames_per_obj.values()) / len(frames_per_obj) if frames_per_obj else 0
            self.filter_log_message(f"- 平均帧数: {avg_frames:.1f} 帧/对象", "info")
            
            # 显示成功消息
            QMessageBox.information(self.main_window, "保存成功", 
                f"筛选结果保存成功！\n\n掩膜保存路径:\n{filtered_masks_dir}\n\n轨迹数据保存路径:\n{excel_path if 'excel_path' in locals() else csv_dir}")
            
            # 隐藏进度条并重新启用保存按钮
            self.main_window.filter_progress_bar.setVisible(False)
            self.main_window.save_filter_btn.setEnabled(True)
            
        except Exception as e:
            import traceback
            error_msg = str(e)
            stack_trace = traceback.format_exc()
            
            self.filter_log_message(f"保存失败: {error_msg}", "error")
            self.filter_log_message(f"堆栈跟踪:\n{stack_trace}", "error")
            
            # 显示错误消息
            QMessageBox.critical(self.main_window, "保存失败", f"保存筛选结果时出错:\n{error_msg}") 
            
            # 隐藏进度条并重新启用保存按钮
            self.main_window.filter_progress_bar.setVisible(False)
            self.main_window.save_filter_btn.setEnabled(True) 