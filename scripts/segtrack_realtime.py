import sys
import os

# 将项目根目录添加到 sys.path
# __file__ 是当前脚本 (segtrack_realtime.py) 的路径
# os.path.dirname(__file__) 是脚本所在的目录 (scripts/)
# os.path.join(os.path.dirname(__file__), '..') 是父目录 (项目根目录)
# os.path.abspath() 获取绝对路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入所需的库
import threading  # 用于创建并发执行的线程
import queue      # 用于线程间安全通信
import cv2        # OpenCV库，用于图像处理和视频捕获
import torch      # PyTorch深度学习框架
import gc         # 垃圾回收模块，用于内存管理
import numpy as np  # 数值计算库
import imageio    # 用于视频写入
from PIL import Image  # 图像处理库

# 导入自定义模块
from models.sam2.sam2.build_sam import build_sam2_video_predictor  # SAM2视频预测器构建函数
from utils.color import COLOR  # 预定义的颜色列表，用于可视化不同对象
from utils.utils import determine_model_cfg  # 根据模型路径确定配置文件


class Lang2SegTrack:
    """
    实时视频分割与追踪类
    实现了用户交互式标注和实时对象追踪功能
    """
    def __init__(self, model_path: str, video_path: str, output_path: str,
                 first_boxes:list[list] | None = None, save_video=True, device="cuda:0"):
        """
        初始化函数
        
        参数:
            model_path: SAM2模型的路径
            video_path: 输入视频的路径
            output_path: 输出视频的路径
            first_boxes: 可选的初始边界框列表
            save_video: 是否保存处理后的视频
            device: 使用的计算设备（'cuda:0'表示第一个GPU）
        """
        # 存储基本参数
        self.model_path = model_path
        self.video_path = video_path
        self.output_path = output_path
        self.save_video = save_video
        self.device = device

        # 初始化状态变量
        self.input_queue = queue.Queue()  # 用于存储用户输入的队列
        if first_boxes is not None:
            self.start = first_boxes  # 初始边界框列表
        else:
            self.start = []
        self.history = []  # 历史追踪对象列表
        self.latest = None  # 最新添加的标注
        self.drawing = False  # 是否正在绘制边界框
        self.add_new = False  # 是否添加了新标注
        self.reset = False  # 是否需要重置追踪状态
        self.ix, self.iy = -1, -1  # 边界框起始点坐标
        self.frame_display = None  # 用于显示的帧
        self.height, self.width = None, None  # 视频尺寸
        
        self.paused = True  # 视频是否暂停，设置为True表示初始状态为暂停
        self.current_frame = None  # 当前帧

    def input_thread(self):
        """
        用户输入处理线程函数
        创建一个独立线程接收用户输入，并将输入放入队列
        """
        while True:
            user_input = input()
            self.input_queue.put(user_input)

    def draw_bbox(self, event, x, y, flags, param):
        """
        鼠标事件回调函数，处理用户的标注操作
        
        参数:
            event: OpenCV鼠标事件类型
            x, y: 鼠标坐标
            flags: 事件标志（如按键状态）
            param: 传递给回调函数的参数（当前帧图像）
        """
        # 只有在暂停状态下才允许标注
        if not self.paused:
            return
            
        if event == cv2.EVENT_LBUTTONDOWN:  # 鼠标左键按下
            if flags & cv2.EVENT_FLAG_CTRLKEY:  # 按住Ctrl键
                # 添加点标注
                self.start.append((x, y))
                self.latest = (x, y)
                self.add_new = True
                cv2.circle(param, (x, y), 5, (0, 255, 0), -1)  # 绘制绿色圆点
            else:
                # 开始绘制边界框
                self.drawing = True
                self.ix, self.iy = x, y  # 记录起始点
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:  # 鼠标移动且正在绘制
            # 实时显示正在绘制的边界框
            img = param.copy()
            cv2.rectangle(img, (self.ix, self.iy), (x, y), (0, 255, 0), 2)
            cv2.imshow("Video Tracking", img)
        elif event == cv2.EVENT_LBUTTONUP and self.drawing:  # 鼠标左键释放
            if abs(x - self.ix) > 2 and abs(y - self.iy) > 2:  # 确保边界框大小合理
                # 完成边界框的绘制
                bbox = [self.ix, self.iy, x, y]
                self.start.append(bbox)
                self.latest = bbox
                self.add_new = True
                cv2.rectangle(param, (self.ix, self.iy), (x, y), (0, 255, 0), 2)
            self.drawing = False  # 结束绘制状态

    def add_to_state(self, predictor, state, list):
        """
        将标注添加到追踪状态中
        
        参数:
            predictor: SAM2预测器对象
            state: 追踪状态字典
            list: 标注列表（可以是点或边界框）
        """
        for id, item in enumerate(list):
            if len(item) == 4:  # 如果是边界框 [x1, y1, x2, y2]
                x1, y1, x2, y2 = item
                # 在显示帧上绘制边界框
                cv2.rectangle(self.frame_display, (x1, y1), (x2, y2), (0, 255, 0), 2)
                # 将边界框添加到SAM2的状态中
                predictor.add_new_points_or_box(state, box=item, frame_idx=state["num_frames"] - 1, obj_id=id)
            else:  # 如果是点 (x, y)
                x, y = item
                # 在显示帧上绘制点
                cv2.circle(self.frame_display, (x, y), 5, (0, 255, 0), -1)
                # 将点转换为张量
                pt = torch.tensor([[x, y]], dtype=torch.float32)
                lbl = torch.tensor([1], dtype=torch.int32)  # 标签1表示前景点
                # 将点添加到SAM2的状态中
                predictor.add_new_points_or_box(state, points=pt, labels=lbl, frame_idx=state["num_frames"] - 1, obj_id=id)

    def track_and_visualize(self, predictor, state, frame, writer):
        """
        执行对象追踪并可视化结果
        
        参数:
            predictor: SAM2预测器对象
            state: 追踪状态字典
            frame: 当前视频帧
            writer: 视频写入器（如果需要保存视频）
        """
        # 检查是否有标注输入
        has_input = any(len(state["point_inputs_per_obj"][i]) > 0 for i in range(len(state["point_inputs_per_obj"])))
        if has_input:
            # 使用SAM2预测器进行推理，得到分割掩码
            for frame_idx, obj_ids, masks in predictor.propagate_in_video(state, state["num_frames"] - 1, 1):
                self.history.clear()
                # 处理每个对象的分割掩码
                for obj_id, mask in zip(obj_ids, masks):
                    # 将掩码转换为布尔数组
                    mask = mask[0].cpu().numpy() > 0.0
                    # 找到掩码中的非零点（对象区域）
                    nonzero = np.argwhere(mask)
                    if nonzero.size == 0:  # 如果掩码为空
                        bbox = [0, 0, 0, 0]
                    else:
                        # 计算边界框坐标
                        y_min, x_min = nonzero.min(axis=0)
                        y_max, x_max = nonzero.max(axis=0)
                        bbox = [x_min, y_min, x_max - x_min, y_max - y_min]  # [x, y, w, h]
                    # 绘制掩码和边界框
                    self.draw_mask_and_bbox(frame, mask, bbox, obj_id)
                    # 记录边界框到历史记录（格式转换为[x1, y1, x2, y2]）
                    self.history.append([bbox[0], bbox[1], bbox[0] + bbox[2], bbox[1] + bbox[3]])
        else:
            # 如果没有标注输入，仅显示当前帧
            cv2.imshow("Video Tracking", self.frame_display)

        # 如果需要保存视频，将当前帧添加到输出视频
        if writer:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # OpenCV使用BGR，而imageio需要RGB
            writer.append_data(rgb)
        
        # 显示暂停/继续状态文本
        if self.paused:
            status_text = "Paused, press SPACE to continue | Annotation enabled"
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            status_text = "Press SPACE to pause | Annotation disabled during playback"
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # 显示处理后的帧
        cv2.imshow("Video Tracking", frame)

    def draw_mask_and_bbox(self, frame, mask, bbox, obj_id):
        """
        在帧上绘制分割掩码和边界框
        
        参数:
            frame: 要绘制的视频帧
            mask: 对象分割掩码（布尔数组）
            bbox: 边界框坐标 [x, y, w, h]
            obj_id: 对象ID，用于确定颜色
        """
        # 创建空白掩码图像
        mask_img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        # 设置掩码颜色（根据对象ID循环使用颜色列表）
        mask_img[mask] = COLOR[obj_id % len(COLOR)]
        # 将掩码叠加到原始帧上，透明度为0.6
        frame[:] = cv2.addWeighted(frame, 1, mask_img, 0.6, 0)
        # 绘制边界框
        x, y, w, h = bbox
        cv2.rectangle(frame, (x, y), (x + w, y + h), COLOR[obj_id % len(COLOR)], 2)
        # 添加对象标签
        cv2.putText(frame, f"obj_{obj_id}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR[obj_id % len(COLOR)], 2)

    def run(self):
        """
        主运行函数，启动视频处理和交互式追踪
        """
        # 根据模型路径确定配置文件
        model_cfg = determine_model_cfg(self.model_path)
        # 构建SAM2视频预测器
        predictor = build_sam2_video_predictor(model_cfg, self.model_path, device=self.device)

        # 打印操作说明
        print("Processing video. Instructions:")
        print("  - SPACE: Pause/Resume video")
        print("  - Mouse drag: Draw bounding box")
        print("  - Ctrl+click: Mark point")
        print("  - Q: Quit program")
        
        # 打开视频文件
        cap = cv2.VideoCapture(self.video_path)
        ret, color_image = cap.read()
        if not ret:
            print("Cannot read video file, please check the path.")
            return

        # 获取视频尺寸
        self.height, self.width = color_image.shape[:2]
        self.current_frame = color_image.copy()

        # 创建视频写入器（如果需要保存视频）
        if self.save_video:
            writer = imageio.get_writer(self.output_path, fps=30)
        else:
            writer = None

        # 创建OpenCV窗口和鼠标回调
        cv2.namedWindow("Video Tracking")
        cv2.setMouseCallback("Video Tracking", self.draw_bbox, param=self.current_frame)
        # 启动用户输入线程
        threading.Thread(target=self.input_thread, daemon=True).start()

        # 使用PyTorch的推理模式和半精度加速
        with torch.inference_mode(), torch.autocast("cuda", dtype=torch.float16):
            # 初始化SAM2状态
            state = predictor.init_state_from_numpy_frames([color_image], offload_video_to_cpu=True)
            # 主循环
            while True:
                if not self.paused:
                    # 如果未暂停，读取下一帧
                    ret, frame = cap.read()
                    if not ret:
                        break  # 视频结束时退出循环
                    self.current_frame = frame.copy()
                else:
                    # 如果暂停，使用当前帧的副本
                    frame = self.current_frame.copy()
                
                # 创建显示帧的副本
                self.frame_display = self.current_frame.copy()
                # 更新鼠标回调函数的参数
                cv2.setMouseCallback("Video Tracking", self.draw_bbox, param=self.frame_display)

                # 处理新添加的标注
                if self.latest and self.add_new:
                    self.history.append(self.latest)
                    self.add_new = False
                    self.reset = True

                # 处理追踪状态的更新
                if len(self.history) > len(self.start) and self.reset:
                    # 如果历史记录有更多对象，重置追踪状态
                    predictor.reset_state(state)
                    self.add_to_state(predictor, state, self.history)
                    self.reset = False
                else:
                    # 否则，添加新标注到当前状态
                    self.add_to_state(predictor, state, self.start)

                # 清空当前标注列表，为下一帧做准备
                self.start.clear()
                
                # 如果未暂停，将当前帧添加到推理状态
                if not self.paused:
                    predictor.append_frame_to_inference_state(state, frame)
                
                # 执行追踪并可视化
                self.track_and_visualize(predictor, state, frame, None if self.paused else writer)

                # 处理键盘输入
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):  # 按Q键退出
                    break
                elif key == ord(' '):  # 空格键切换暂停状态
                    self.paused = not self.paused
                    print("Video " + ("paused" if self.paused else "resumed"))

        # 释放资源
        cap.release()
        if writer:
            writer.close()
        cv2.destroyAllWindows()
        # 清理模型和状态对象
        del predictor, state
        # 垃圾回收和GPU内存清理
        gc.collect()
        torch.clear_autocast_cache()
        torch.cuda.empty_cache()


if __name__ == "__main__":
    # 创建并运行追踪器实例
    tracker = Lang2SegTrack(
        model_path="models/sam2/checkpoints/sam2.1_hiera_tiny.pt",  # SAM2模型路径（使用tiny版本）
        video_path="assets/05_default_juggle.mp4",  # 输入视频路径
        output_path="processed_video.mp4",  # 输出视频路径
        save_video=True  # 保存处理后的视频
    )
    tracker.run()
