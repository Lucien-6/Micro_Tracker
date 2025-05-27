import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QDateTime
import time
import os
from pathlib import Path
import math
import traceback
from PyQt5.QtGui import QColor

class FilterMaskThread(QThread):
    """掩膜筛选线程，用于分析、筛选掩膜并生成预览视频"""
    progress_update = pyqtSignal(str)  # 进度更新信号
    progress_percent = pyqtSignal(int)  # 进度百分比信号
    filter_finished = pyqtSignal(bool, str)  # 筛选完成信号，参数为(成功与否, 消息)
    frame_processed = pyqtSignal(np.ndarray, int, int)  # 帧处理信号，参数为(帧, 当前索引, 总帧数)
    stats_update = pyqtSignal(int, int)  # 统计信息更新信号，参数为(总对象数, 通过筛选的对象数)
    
    def __init__(self, masks_dir, fps=1.0, um_per_pixel=1.0, filter_params=None):
        super().__init__()
        self.masks_dir = masks_dir
        self.fps = fps
        self.um_per_pixel = um_per_pixel
        self.filter_params = filter_params or {}
        self.is_running = True
        
        # 存储筛选结果
        self.filtered_masks = []  # 存储筛选后的掩膜数据
        self.object_trajectories = {}  # 存储对象轨迹数据
        self.filtered_metadata = {}  # 存储已筛选对象的元数据(面积、中心点、长轴、短轴、角度等)
        
        # 处理中间数据
        self.all_masks = []  # 所有掩膜文件
        self.total_objects = 0  # 总对象数
        self.passed_objects = 0  # 通过筛选的对象数
        self.original_masks = []  # 原始掩膜数据
        
        # 添加记录对象筛选结果和原因的字典
        self.object_filter_results = {}  # 格式: {obj_id: {"result": "passed|filtered|truncated", "reason": "原因描述"}}
    
    def run(self):
        try:
            self.progress_update.emit("正在加载掩膜图片...")
            self.progress_percent.emit(0)
            
            # 1. 加载所有掩膜图片
            mask_files = sorted([f for f in os.listdir(self.masks_dir) if f.endswith('.png') and f.startswith('frame_')])
            if not mask_files:
                raise Exception(f"未在 {self.masks_dir} 中找到掩膜图片")
            
            self.all_masks = mask_files
            total_frames = len(mask_files)
            self.progress_update.emit(f"找到 {total_frames} 个掩膜图片")
            
            # 2. 分析所有掩膜，提取对象ID和轨迹
            self.progress_update.emit("正在分析掩膜数据...")
            
            # 首先读取所有掩膜数据
            masks_data = []
            object_ids = set()
            
            for i, mask_file in enumerate(mask_files):
                # 更新进度
                percent = int((i / total_frames) * 30)  # 占总进度的30%
                self.progress_percent.emit(percent)
                
                # 读取掩膜
                mask_path = os.path.join(self.masks_dir, mask_file)
                mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
                
                if mask is None:
                    self.progress_update.emit(f"警告: 无法读取掩膜文件 {mask_file}")
                    continue
                
                # 提取当前掩膜中的所有对象ID
                unique_ids = np.unique(mask)
                unique_ids = unique_ids[unique_ids > 0]  # 排除背景(值为0)
                
                # 更新所有对象ID集合
                for obj_id in unique_ids:
                    object_ids.add(int(obj_id))
                
                # 存储掩膜数据
                masks_data.append(mask)
                
                # 每处理10个掩膜更新一次日志
                if i % 10 == 0 or i == total_frames - 1:
                    self.progress_update.emit(f"已处理 {i+1}/{total_frames} 个掩膜图片")
            
            self.original_masks = masks_data
            self.total_objects = len(object_ids)
            self.progress_update.emit(f"共检测到 {self.total_objects} 个对象")
            
            # 3. 应用筛选条件
            self.progress_update.emit("开始应用筛选条件...")
            
            # 初始化每个对象的有效帧范围 (默认全部有效)
            object_valid_frames = {obj_id: (0, total_frames-1) for obj_id in object_ids}
            
            # 收集所有对象的轨迹数据
            self.progress_update.emit("正在计算对象属性...")
            
            # 存储所有对象在每一帧的数据
            object_data = {obj_id: [] for obj_id in object_ids}
            
            # 对每一帧处理
            for frame_idx, mask in enumerate(masks_data):
                # 更新进度
                percent = 30 + int((frame_idx / total_frames) * 30)  # 占总进度的30%到60%
                self.progress_percent.emit(percent)
                
                # 处理当前帧中的每个对象
                frame_objects = np.unique(mask)
                frame_objects = frame_objects[frame_objects > 0]  # 排除背景(值为0)
                
                for obj_id in frame_objects:
                    # 提取当前对象的掩膜
                    obj_mask = (mask == obj_id).astype(np.uint8) * 255
                    
                    # 计算对象的位置和形状
                    contours, _ = cv2.findContours(obj_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    if not contours:
                        continue
                    
                    # 获取最大轮廓
                    largest_contour = max(contours, key=cv2.contourArea)
                    
                    # 计算面积 (单位: μm²)
                    area_pixels = cv2.contourArea(largest_contour)
                    area_um2 = area_pixels * (self.um_per_pixel ** 2)
                    
                    # 计算质心
                    M = cv2.moments(largest_contour)
                    if M["m00"] == 0:
                        continue
                    
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    # 转换为实际单位 (μm)
                    cx_um = cx * self.um_per_pixel
                    cy_um = cy * self.um_per_pixel
                    
                    # 尝试椭圆拟合
                    major_axis = 0
                    minor_axis = 0
                    angle = 0
                    
                    if len(largest_contour) >= 5:  # 需要至少5个点才能拟合椭圆
                        try:
                            ellipse = cv2.fitEllipse(largest_contour)
                            center, axes, angle = ellipse
                            
                            # 转换为实际单位 (μm)
                            major_axis = max(axes) * self.um_per_pixel / 2
                            minor_axis = min(axes) * self.um_per_pixel / 2
                            
                            # 确保角度在0-180度范围内
                            angle = angle % 180
                        except:
                            pass
                    
                    # 检查是否接触边界
                    touches_boundary = self._check_touches_boundary(obj_mask)
                    
                    # 存储数据
                    frame_data = {
                        'frame': frame_idx,
                        'time': frame_idx / self.fps,  # 添加time字段，单位为秒
                        'area': area_um2,
                        'center_x': cx_um,
                        'center_y': cy_um,
                        'center_x_px': cx,
                        'center_y_px': cy,
                        'major_axis': major_axis,
                        'minor_axis': minor_axis,
                        'angle': angle,
                        'touches_boundary': touches_boundary,
                        'contour': largest_contour
                    }
                    
                    object_data[obj_id].append(frame_data)
                
                # 每处理10个掩膜更新一次日志
                if frame_idx % 10 == 0 or frame_idx == total_frames - 1:
                    self.progress_update.emit(f"计算对象属性: {frame_idx+1}/{total_frames}")
            
            # 4. 应用筛选条件
            self.progress_update.emit("正在应用筛选条件...")
            excluded_ids = set()
            
            # 4.0 排除指定对象ID
            if 'exclude_ids' in self.filter_params and self.filter_params['exclude_ids']:
                excluded_ids.update(self.filter_params['exclude_ids'])
                self.progress_update.emit(f"已排除指定对象: {self.filter_params['exclude_ids']}")
                
                # 记录排除原因
                for obj_id in self.filter_params['exclude_ids']:
                    self.object_filter_results[obj_id] = {
                        "result": "filtered", 
                        "reason": "用户手动排除"
                    }
            
            # 保存通过筛选的对象
            valid_objects = {}
            
            # 对每个对象应用筛选条件
            for obj_id in object_ids:
                # 如果对象在排除列表中，则跳过
                if obj_id in excluded_ids:
                    continue
                
                # 获取对象的所有帧数据
                obj_frames = object_data.get(obj_id, [])
                if not obj_frames:
                    # 记录对象筛选结果
                    self.object_filter_results[obj_id] = {
                        "result": "filtered", 
                        "reason": "未找到对象数据"
                    }
                    continue
                
                # 记录初始帧数
                original_frame_count = len(obj_frames)
                valid_frame_indices = list(range(len(obj_frames)))
                truncated = False
                reason = "通过所有筛选条件"
                
                # 4.1 应用面积区间筛选
                if self.filter_params.get('area_filter', False):
                    area_min = self.filter_params.get('area_min', 0)
                    area_max = self.filter_params.get('area_max', float('inf'))
                    
                    # 找出不符合面积条件的帧索引
                    invalid_indices = []
                    for idx, frame_data in enumerate(obj_frames):
                        if not (area_min <= frame_data['area'] <= area_max):
                            invalid_indices.append(idx)
                    
                    # 如果所有帧都不符合条件，则排除该对象
                    if len(invalid_indices) == len(obj_frames):
                        # 记录对象筛选结果
                        self.object_filter_results[obj_id] = {
                            "result": "filtered", 
                            "reason": f"面积不在指定范围内 ({area_min}~{area_max} μm²)"
                        }
                        excluded_ids.add(obj_id)
                        continue
                    
                    # 如果只有部分帧不符合条件，标记轨迹截断点
                    if invalid_indices:
                        # 找出第一个不符合条件的帧
                        first_invalid = min(invalid_indices)
                        valid_frame_indices = valid_frame_indices[:first_invalid]
                        truncated = True
                        reason = f"面积不在指定范围内 ({area_min}~{area_max} μm²)"
                
                # 面积区间筛选后，更新valid_start和valid_end
                if valid_frame_indices:
                    valid_start = valid_frame_indices[0] 
                    valid_end = valid_frame_indices[-1]
                else:
                    # 如果没有有效帧，标记为无效对象
                    valid_start = 0
                    valid_end = -1
                
                # 4.2 应用面积变化率筛选
                if self.filter_params.get('area_change_filter', False) and len(valid_frame_indices) > 1:
                    area_change_threshold = self.filter_params.get('area_change_threshold', 0.5)
                    
                    # 使用valid_frame_indices进行遍历
                    for i in range(1, len(valid_frame_indices)):
                        prev_idx = valid_frame_indices[i-1]
                        curr_idx = valid_frame_indices[i]
                        
                        prev_area = obj_frames[prev_idx]['area']
                        curr_area = obj_frames[curr_idx]['area']
                        
                        # 计算较小面积与较大面积的比值
                        if prev_area > 0 and curr_area > 0:
                            area_ratio = min(prev_area, curr_area) / max(prev_area, curr_area)
                            
                            if area_ratio < area_change_threshold:
                                # 截断到当前帧的前一帧
                                valid_frame_indices = valid_frame_indices[:i]
                                valid_end = valid_frame_indices[-1]  # 更新valid_end
                                truncated = True
                                # 记录截断原因和位置
                                frame_time = obj_frames[curr_idx]['frame'] / self.fps
                                self.object_filter_results[obj_id] = {
                                    "result": "truncated", 
                                    "reason": f"在第{curr_idx+1}帧(时刻{frame_time:.2f}s)处面积变化率({area_ratio:.3f})低于阈值({area_change_threshold})",
                                    "truncated_at": valid_end,
                                    "original_frames": len(obj_frames)
                                }
                                break
                
                # 4.3 应用瞬时速度区间筛选
                if self.filter_params.get('velocity_filter', False) and len(valid_frame_indices) > 1:
                    velocity_min = self.filter_params.get('velocity_min', 0)
                    velocity_max = self.filter_params.get('velocity_max', float('inf'))
                    
                    # 使用valid_frame_indices进行遍历
                    for i in range(1, len(valid_frame_indices)):
                        prev_idx = valid_frame_indices[i-1]
                        curr_idx = valid_frame_indices[i]
                        
                        prev_data = obj_frames[prev_idx]
                        curr_data = obj_frames[curr_idx]
                        
                        # 计算两帧之间的时间差(秒)
                        time_diff = (curr_data['frame'] - prev_data['frame']) / self.fps
                        
                        # 计算两帧之间的位移(μm)
                        dx = curr_data['center_x'] - prev_data['center_x']
                        dy = curr_data['center_y'] - prev_data['center_y']
                        distance = math.sqrt(dx**2 + dy**2)
                        
                        # 计算瞬时速度(μm/s)
                        if time_diff > 0:
                            velocity = distance / time_diff
                            
                            if velocity < velocity_min or velocity > velocity_max:
                                # 截断到当前帧的前一帧
                                valid_frame_indices = valid_frame_indices[:i]
                                valid_end = valid_frame_indices[-1]  # 更新valid_end
                                truncated = True
                                # 记录截断原因和位置
                                frame_time = curr_data['frame'] / self.fps
                                self.object_filter_results[obj_id] = {
                                    "result": "truncated", 
                                    "reason": f"在第{curr_idx+1}帧(时刻{frame_time:.2f}s)处瞬时速度({velocity:.2f} μm/s)超出范围({velocity_min}~{velocity_max} μm/s)",
                                    "truncated_at": valid_end,
                                    "original_frames": len(obj_frames)
                                }
                                break
                
                # 4.4 应用总位移区间筛选（整个轨迹的首尾位移）
                if self.filter_params.get('displacement_filter', False) and len(valid_frame_indices) > 1:
                    displacement_min = self.filter_params.get('displacement_min', 0)
                    displacement_max = self.filter_params.get('displacement_max', float('inf'))
                    
                    # 计算首帧和尾帧之间的位移
                    first_idx = valid_frame_indices[0]
                    last_idx = valid_frame_indices[-1]
                    
                    first_data = obj_frames[first_idx]
                    last_data = obj_frames[last_idx]
                    
                    dx = last_data['center_x'] - first_data['center_x']
                    dy = last_data['center_y'] - first_data['center_y']
                    displacement = math.sqrt(dx**2 + dy**2)
                    
                    # 如果总位移超出范围，排除该对象
                    if not (displacement_min <= displacement <= displacement_max):
                        # 记录对象筛选结果
                        self.object_filter_results[obj_id] = {
                            "result": "filtered", 
                            "reason": f"总位移超出范围 [{displacement_min}-{displacement_max}] μm"
                        }
                        excluded_ids.add(obj_id)
                        continue
                
                # 4.5 应用边界截断排除
                if self.filter_params.get('boundary_filter', False) and valid_frame_indices:
                    truncated = False
                    
                    # 对每个有效帧检查是否接触边界
                    for i, idx in enumerate(valid_frame_indices):
                        frame_data = obj_frames[idx]
                        
                        if frame_data['touches_boundary']:
                            # 截断到当前帧的前一帧
                            if i > 0:
                                valid_frame_indices = valid_frame_indices[:i]
                                valid_end = valid_frame_indices[-1]  # 更新valid_end
                                truncated = True
                                # 记录截断原因和位置
                                frame_time = frame_data['frame'] / self.fps
                                self.object_filter_results[obj_id] = {
                                    "result": "truncated", 
                                    "reason": f"在第{idx+1}帧(时刻{frame_time:.2f}s)处接触图像边界",
                                    "truncated_at": valid_end,
                                    "original_frames": len(obj_frames)
                                }
                                break
                
                # 4.6 相互最短距离筛选
                if self.filter_params.get('min_distance_filter', False) and valid_frame_indices:
                    min_distance_threshold = self.filter_params.get('min_distance_threshold', 10)
                    truncated = False
                    
                    # 对每一帧检查，使用valid_frame_indices
                    for i, frame_idx in enumerate(valid_frame_indices):
                        # 获取当前帧的所有对象
                        current_frame_objects = {}
                        for other_id in object_ids:
                            if other_id == obj_id:
                                continue
                                
                            # 找到该对象在当前帧的数据
                            other_frame_data = None
                            for data in object_data.get(other_id, []):
                                if data['frame'] == obj_frames[frame_idx]['frame']:
                                    other_frame_data = data
                                    break
                            
                            if other_frame_data:
                                current_frame_objects[other_id] = other_frame_data
                        
                        # 计算与其他对象的距离
                        obj_contour = obj_frames[frame_idx]['contour']
                        obj_mask_position = None
                        
                        too_close = False
                        close_obj_id = None
                        min_distance_found = float('inf')
                        
                        for other_id, other_data in current_frame_objects.items():
                            other_contour = other_data['contour']
                            
                            # 计算两个轮廓之间的最短距离
                            min_dist = self._calculate_contour_distance(obj_contour, other_contour)
                            
                            # 转换为实际距离 (μm)
                            min_dist_um = min_dist * self.um_per_pixel
                            
                            if min_dist_um < min_distance_threshold and min_dist_um < min_distance_found:
                                too_close = True
                                close_obj_id = other_id
                                min_distance_found = min_dist_um
                        
                        if too_close:
                            # 截断到当前帧的前一帧
                            if i > 0:
                                valid_frame_indices = valid_frame_indices[:i]
                                valid_end = valid_frame_indices[-1]  # 更新valid_end
                                truncated = True
                                # 记录截断原因和位置
                                frame_time = obj_frames[frame_idx]['frame'] / self.fps
                                self.object_filter_results[obj_id] = {
                                    "result": "truncated", 
                                    "reason": f"在第{frame_idx+1}帧(时刻{frame_time:.2f}s)处与对象{close_obj_id}的距离({min_distance_found:.2f} μm)小于阈值({min_distance_threshold} μm)",
                                    "truncated_at": valid_end,
                                    "original_frames": len(obj_frames)
                                }
                                break
                
                # 检查是否有有效帧
                if not valid_frame_indices:
                    # 记录对象筛选结果
                    self.object_filter_results[obj_id] = {
                        "result": "filtered", 
                        "reason": reason
                    }
                    excluded_ids.add(obj_id)
                    continue
                
                # 保存有效帧数据
                valid_frames = [obj_frames[i] for i in valid_frame_indices]
                valid_objects[obj_id] = valid_frames
                
                # 如果对象通过所有筛选条件
                if obj_id not in self.object_filter_results:
                    self.object_filter_results[obj_id] = {
                        "result": "passed", 
                        "reason": "通过所有筛选条件",
                        "frames": len(valid_frames),
                        "original_frames": len(obj_frames)
                    }
                # 如果是截断状态，确保包含frames字段
                elif self.object_filter_results[obj_id]["result"] == "truncated":
                    self.object_filter_results[obj_id]["frames"] = len(valid_frames)
                    if "original_frames" not in self.object_filter_results[obj_id]:
                        self.object_filter_results[obj_id]["original_frames"] = len(obj_frames)
            
            # 更新统计信息
            self.passed_objects = len(valid_objects)
            self.stats_update.emit(self.total_objects, self.passed_objects)
            self.progress_update.emit(f"筛选结果: {self.passed_objects}/{self.total_objects} 个对象通过筛选")
            
            # 5. 生成筛选后的可视化结果
            self.progress_update.emit("正在生成筛选结果可视化...")
            
            # 为每个有效对象分配颜色
            colors = []
            for i in range(30):  # 预设30种颜色
                h = i * 12 % 180  # 色调均匀分布在0-180之间
                s = 200  # 饱和度固定
                v = 255  # 明度固定
                
                # 转换为RGB
                c = QColor()
                c.setHsv(h, s, v)
                r, g, b = c.red(), c.green(), c.blue()
                colors.append((r, g, b))
            
            # 随机打乱颜色
            np.random.shuffle(colors)
            
            # 为每个有效对象分配颜色
            object_colors = {}
            for i, obj_id in enumerate(valid_objects.keys()):
                object_colors[obj_id] = colors[i % len(colors)]
            
            # 为每帧创建可视化图像
            filtered_viz_frames = []
            h, w = masks_data[0].shape[:2]  # 获取掩膜尺寸
            
            # 对每一帧生成筛选后的掩膜
            for frame_idx in range(total_frames):
                # 更新进度
                percent = 60 + int((frame_idx / total_frames) * 40)  # 占总进度的60%到100%
                self.progress_percent.emit(percent)
                
                # 创建空白掩膜
                original_mask = masks_data[frame_idx]
                
                # 创建彩色输出图像
                colored_mask = np.zeros((h, w, 3), dtype=np.uint8)
                
                # 存储该帧各对象的轨迹点
                frame_trajectory_points = {}
                
                # 处理每个有效对象
                for obj_id, frames in valid_objects.items():
                    # 在对象数据中找到当前帧
                    frame_data = next((fd for fd in frames if fd['frame'] == frame_idx), None)
                    if frame_data is None:
                        continue
                    
                    # 提取对象掩膜
                    obj_mask = (original_mask == obj_id).astype(np.uint8) * 255
                    
                    # 为对象着色
                    color = object_colors.get(obj_id, (255, 255, 255))
                    colored_mask[obj_mask > 0] = color
                    
                    # 获取对象轨迹点以绘制轨迹
                    trajectory_points = []
                    for prev_fd in frames:
                        if prev_fd['frame'] <= frame_idx:
                            point = (prev_fd['center_x_px'], prev_fd['center_y_px'])
                            trajectory_points.append(point)
                    
                    frame_trajectory_points[obj_id] = {
                        'points': trajectory_points,
                        'color': color,
                        'center': (frame_data['center_x_px'], frame_data['center_y_px']),
                        'major_axis': frame_data['major_axis'],
                        'minor_axis': frame_data['minor_axis'],
                        'angle': frame_data['angle'],
                        'contour': frame_data.get('contour')  # 安全获取轮廓信息
                    }
                
                # 绘制轨迹和特征
                vis_mask = colored_mask.copy()
                
                # 先保存所有对象的ID标签参数，以便最后绘制在最上层
                id_labels = []
                
                # 绘制轨迹和中心点
                for obj_id, trajectory_data in frame_trajectory_points.items():
                    points = trajectory_data['points']
                    color = trajectory_data['color']
                    center = trajectory_data['center']
                    major_axis = trajectory_data['major_axis']
                    minor_axis = trajectory_data['minor_axis']
                    angle = trajectory_data['angle']
                    
                    # 绘制轨迹
                    if len(points) > 1:
                        for i in range(1, len(points)):
                            pt1 = tuple(map(int, points[i-1]))
                            pt2 = tuple(map(int, points[i]))
                            cv2.line(vis_mask, pt1, pt2, color, 2)
                    
                    # 收集对象ID标签信息，但暂不绘制
                    center_pt = tuple(map(int, center))
                    # 创建ID标签文本
                    id_text = str(obj_id)
                    # 计算文本大小以进行居中放置
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    font_scale = 1.0  # 调整为较小的字体大小
                    thickness = 2     # 调整为较细的线条粗细
                    (text_width, text_height), baseline = cv2.getTextSize(id_text, font, font_scale, thickness)
                    # 计算文本位置使其居中
                    text_x = int(center_pt[0] - text_width/2)
                    text_y = int(center_pt[1] + text_height/2)
                    # 保存标签信息，稍后绘制
                    id_labels.append((id_text, (text_x, text_y), font, font_scale, thickness))
                    
                    # 绘制主轴（红色）和次轴（蓝色）
                    if major_axis > 0 and minor_axis > 0:
                        # 转换为像素单位
                        major_axis_px = major_axis / self.um_per_pixel
                        minor_axis_px = minor_axis / self.um_per_pixel
                        
                        # 获取椭圆原始参数
                        ellipse_data = None
                        
                        # 重新获取轮廓并拟合椭圆以确保正确性
                        contour = trajectory_data.get('contour')
                        if contour is not None and len(contour) >= 5:  # 需要至少5个点才能拟合椭圆
                            try:
                                ellipse = cv2.fitEllipse(contour)
                                center_point, axes_len, ellipse_angle = ellipse
                                
                                # 判断哪个是主轴（较长的轴）
                                is_width_major = axes_len[0] > axes_len[1]
                                
                                # 如果宽是主轴，则角度不变；如果高是主轴，则角度加90度
                                if is_width_major:
                                    major_angle = ellipse_angle
                                else:
                                    major_angle = (ellipse_angle + 90) % 180
                                    
                                # 次轴垂直于主轴
                                minor_angle = (major_angle + 90) % 180
                                
                                # 转换角度为弧度
                                major_angle_rad = np.deg2rad(major_angle)
                                minor_angle_rad = np.deg2rad(minor_angle)
                                
                                # 计算主轴端点
                                dx_major = major_axis_px * np.cos(major_angle_rad)
                                dy_major = major_axis_px * np.sin(major_angle_rad)
                                
                                # 计算次轴端点
                                dx_minor = minor_axis_px * np.cos(minor_angle_rad)
                                dy_minor = minor_axis_px * np.sin(minor_angle_rad)
                                
                                # 绘制主轴（红色）
                                pt1_major = (int(center[0] - dx_major), int(center[1] - dy_major))
                                pt2_major = (int(center[0] + dx_major), int(center[1] + dy_major))
                                cv2.line(vis_mask, pt1_major, pt2_major, (0, 0, 255), 2)
                                
                                # 绘制次轴（蓝色）
                                pt1_minor = (int(center[0] - dx_minor), int(center[1] - dy_minor))
                                pt2_minor = (int(center[0] + dx_minor), int(center[1] + dy_minor))
                                cv2.line(vis_mask, pt1_minor, pt2_minor, (255, 0, 0), 2)
                            except:
                                # 如果重新拟合失败，使用简化的方法
                                angle_rad = np.deg2rad(angle)
                                
                                # 计算主轴端点
                                dx_major = major_axis_px * np.cos(angle_rad)
                                dy_major = major_axis_px * np.sin(angle_rad)
                                
                                # 计算次轴端点（垂直于主轴）
                                dx_minor = minor_axis_px * np.cos(angle_rad + np.pi/2)
                                dy_minor = minor_axis_px * np.sin(angle_rad + np.pi/2)
                                
                                # 绘制主轴（红色）
                                pt1_major = (int(center[0] - dx_major), int(center[1] - dy_major))
                                pt2_major = (int(center[0] + dx_major), int(center[1] + dy_major))
                                cv2.line(vis_mask, pt1_major, pt2_major, (0, 0, 255), 2)
                                
                                # 绘制次轴（蓝色）
                                pt1_minor = (int(center[0] - dx_minor), int(center[1] - dy_minor))
                                pt2_minor = (int(center[0] + dx_minor), int(center[1] + dy_minor))
                                cv2.line(vis_mask, pt1_minor, pt2_minor, (255, 0, 0), 2)
                
                # 最后，在所有绘制完成后，绘制ID标签，确保它们位于最上层
                for id_text, pos, font, font_scale, thickness in id_labels:
                    # 绘制白色文本
                    cv2.putText(vis_mask, id_text, pos, font, font_scale, (255, 255, 255), thickness)
                
                # 添加到筛选后的掩膜列表
                filtered_viz_frames.append(vis_mask)
                
                # 每处理10帧更新一次日志
                if frame_idx % 10 == 0 or frame_idx == total_frames - 1:
                    self.progress_update.emit(f"生成可视化帧: {frame_idx+1}/{total_frames}")
                    
                    # 实时显示当前处理的帧
                    if filtered_viz_frames:
                        self.frame_processed.emit(filtered_viz_frames[-1], frame_idx, total_frames)
            
            # 保存最终结果
            self.filtered_masks = filtered_viz_frames
            self.object_trajectories = valid_objects
            
            # 统计完全通过筛选和部分截断的对象
            passed_count = 0
            truncated_count = 0
            for obj_id, result in self.object_filter_results.items():
                if result['result'] == 'passed':
                    passed_count += 1
                elif result['result'] == 'truncated':
                    truncated_count += 1
            
            # 通过筛选数量包括完全通过和部分截断的对象
            self.passed_objects = passed_count + truncated_count
            
            # 发送统计信息
            self.stats_update.emit(self.total_objects, self.passed_objects)
            
            # 完成筛选
            self.progress_percent.emit(100)
            self.progress_update.emit(f"筛选完成! 原始对象数: {self.total_objects}, 通过筛选: {self.passed_objects} (完全通过: {passed_count}, 部分截断: {truncated_count})")
            
            # 预览第一帧
            if self.filtered_masks:
                self.frame_processed.emit(self.filtered_masks[0], 0, len(self.filtered_masks))
            
            # 处理完成，发出成功信号
            success_message = f"筛选完成！从 {self.total_objects} 个对象中筛选出 {self.passed_objects} 个对象"
            self.filter_finished.emit(True, success_message)
            
        except Exception as e:
            # 出现异常，发出失败信号
            error_message = str(e)
            stack_trace = traceback.format_exc()
            
            self.progress_update.emit(f"错误: {error_message}")
            self.progress_update.emit(f"堆栈跟踪:\n{stack_trace}")
            self.filter_finished.emit(False, error_message)
    
    def _check_touches_boundary(self, mask):
        """检查掩膜是否接触图像边界"""
        h, w = mask.shape[:2]
        
        # 检查四个边界
        top_edge = mask[0, :]
        bottom_edge = mask[h-1, :]
        left_edge = mask[:, 0]
        right_edge = mask[:, w-1]
        
        # 如果任何边界上有掩膜像素，则认为接触边界
        return np.any(top_edge) or np.any(bottom_edge) or np.any(left_edge) or np.any(right_edge)
    
    def _calculate_contour_distance(self, contour1, contour2):
        """计算两个轮廓间的最短距离"""
        min_distance = float('inf')
        
        # 简化计算，每隔几个点采样
        step = max(1, len(contour1) // 20)
        
        for i in range(0, len(contour1), step):
            pt1 = contour1[i][0]
            
            for j in range(0, len(contour2), step):
                pt2 = contour2[j][0]
                
                # 计算两点间距离
                dist = np.sqrt((pt1[0] - pt2[0])**2 + (pt1[1] - pt2[1])**2)
                
                if dist < min_distance:
                    min_distance = dist
        
        return min_distance 