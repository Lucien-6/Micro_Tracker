import cv2
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QDateTime

class VideoThread(QThread):
    """视频读取线程，用于显示视频第一帧和滑动浏览视频帧"""
    frame_ready = pyqtSignal(np.ndarray)
    frame_index_changed = pyqtSignal(int)  # 添加帧索引变化信号
    
    def __init__(self, video_path):
        super().__init__()
        self.video_path = video_path
        self.running = True
        self.paused = True  # 默认启动时处于暂停状态
        self.frame_index = 0
        self.total_frames = 0
        self.fps = 30  # 默认帧率，会在run()中更新为实际帧率
        self.frame_time_ms = 33  # 默认帧间隔(毫秒)，会在run()中更新
        self.cap = None
        self.mutex = QMutex()  # 添加互斥锁保护共享数据
        self.frame_changed = False  # 标记是否请求了新帧
        self.last_frame_time = 0  # 上一帧的时间戳
        
    def run(self):
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            print(f"Error: Could not open video file {self.video_path}")
            return
            
        # 获取视频信息
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.fps <= 0:
            self.fps = 30  # 如果无法获取帧率，使用默认值
        
        # 计算帧间隔时间(毫秒)
        self.frame_time_ms = int(1000 / self.fps)
        
        # 立即读取第一帧
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = self.cap.read()
        if ret:
            self.frame_ready.emit(frame)
            self.frame_index_changed.emit(0)  # 发送初始帧索引信号
        
        self.last_frame_time = QDateTime.currentMSecsSinceEpoch()
        
        while self.running:
            current_time = QDateTime.currentMSecsSinceEpoch()
            
            self.mutex.lock()
            paused = self.paused
            current_index = self.frame_index
            frame_changed = self.frame_changed
            self.frame_changed = False  # 重置标志
            self.mutex.unlock()
            
            if not paused or frame_changed:
                # 设置视频位置并读取帧
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_index)
                ret, frame = self.cap.read()
                
                if ret:
                    self.frame_ready.emit(frame)
                    self.frame_index_changed.emit(current_index)  # 发送帧索引变化信号
                    
                    # 更新时间戳
                    self.last_frame_time = current_time
                    
                    # 如果不是暂停状态且没有特定帧的请求，则自动前进到下一帧
                    if not paused and not frame_changed:
                        self.mutex.lock()
                        next_index = (current_index + 1) % self.total_frames
                        self.frame_index = next_index
                        self.mutex.unlock()
                    
                else:
                    # 读取失败，可能到达视频末尾，回到开始
                    self.mutex.lock()
                    self.frame_index = 0
                    if not paused:  # 如果是自动播放模式，则循环播放
                        self.frame_changed = True  # 标记需要重新加载第一帧
                    else:
                        self.paused = True  # 如果是手动模式，则暂停
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
        
        if self.cap:
            self.cap.release()
    
    def stop(self):
        """停止线程并等待其结束"""
        self.running = False
        self.wait()
    
    def set_frame_index(self, index):
        """设置要显示的帧索引"""
        self.mutex.lock()
        self.frame_index = max(0, min(index, self.total_frames - 1))
        self.frame_changed = True  # 标记需要切换到新帧
        self.mutex.unlock()
        
    def toggle_pause(self):
        """切换暂停/播放状态"""
        self.mutex.lock()
        self.paused = not self.paused
        # 重置时间戳，保证从暂停恢复播放时帧率正确
        if not self.paused:
            self.last_frame_time = QDateTime.currentMSecsSinceEpoch()
        self.mutex.unlock() 