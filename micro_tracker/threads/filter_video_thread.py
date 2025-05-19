import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QDateTime

class FilterVideoThread(QThread):
    """筛选结果视频播放线程"""
    frame_ready = pyqtSignal(np.ndarray)
    frame_index_changed = pyqtSignal(int)
    
    def __init__(self, filtered_masks):
        super().__init__()
        self.filtered_masks = filtered_masks
        self.running = True
        self.paused = True
        self.frame_index = 0
        self.total_frames = len(filtered_masks) if filtered_masks else 0
        self.fps = 10  # 默认播放帧率
        self.frame_time_ms = int(1000 / self.fps)
        self.mutex = QMutex()
        self.frame_changed = False
        self.last_frame_time = 0
    
    def run(self):
        if not self.filtered_masks:
            return
            
        # 设置初始帧
        self.frame_ready.emit(self.filtered_masks[0])
        self.frame_index_changed.emit(0)
        
        self.last_frame_time = QDateTime.currentMSecsSinceEpoch()
        
        while self.running:
            current_time = QDateTime.currentMSecsSinceEpoch()
            
            self.mutex.lock()
            paused = self.paused
            current_index = self.frame_index
            frame_changed = self.frame_changed
            self.frame_changed = False
            self.mutex.unlock()
            
            if not paused or frame_changed:
                # 发送当前帧
                self.frame_ready.emit(self.filtered_masks[current_index])
                self.frame_index_changed.emit(current_index)
                
                # 更新时间戳
                self.last_frame_time = current_time
                
                # 如果不是暂停状态且没有特定帧的请求，则自动前进到下一帧
                if not paused and not frame_changed:
                    self.mutex.lock()
                    next_index = (current_index + 1) % self.total_frames
                    self.frame_index = next_index
                    self.mutex.unlock()
            
            # 计算下一帧应该等待的时间
            if not paused:
                # 基于上一帧的时间和帧率计算下一帧应显示的时间
                next_frame_time = self.last_frame_time + self.frame_time_ms
                current_time = QDateTime.currentMSecsSinceEpoch()
                
                # 计算需要等待的时间
                wait_time = next_frame_time - current_time
                
                # 如果需要等待，则等待合适的时间；否则立即处理下一帧
                if wait_time > 1:
                    self.msleep(int(wait_time))
                else:
                    # 如果处理时间已经超过了帧间隔，至少休眠1毫秒避免CPU占用过高
                    self.msleep(1)
            else:
                # 如果暂停，则较长时间休眠以减少CPU使用
                self.msleep(100)
    
    def stop(self):
        self.running = False
        self.wait()
    
    def set_frame_index(self, index):
        """设置要显示的帧索引"""
        self.mutex.lock()
        self.frame_index = max(0, min(index, self.total_frames - 1))
        self.frame_changed = True
        self.mutex.unlock()
    
    def toggle_pause(self):
        """切换暂停/播放状态"""
        self.mutex.lock()
        self.paused = not self.paused
        # 重置时间戳，保证从暂停恢复播放时帧率正确
        if not self.paused:
            self.last_frame_time = QDateTime.currentMSecsSinceEpoch()
        self.mutex.unlock()
    
    def set_fps(self, fps):
        """设置播放帧率"""
        self.mutex.lock()
        self.fps = max(1, fps)
        self.frame_time_ms = int(1000 / self.fps)
        self.mutex.unlock() 