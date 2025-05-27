from PyQt5.QtWidgets import QTextEdit, QVBoxLayout
from PyQt5.QtCore import Qt

from micro_tracker.ui.base_tab import BaseTab

class GuideTab(BaseTab):
    """使用指南标签页类"""
    
    def __init__(self, main_window):
        """
        初始化使用指南标签页
        
        Args:
            main_window: 主窗口引用
        """
        super().__init__(main_window)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI界面"""
        # 整体布局
        guide_layout = QVBoxLayout(self)
        guide_layout.setContentsMargins(15, 15, 15, 15)
        
        guide_text = QTextEdit()
        guide_text.setReadOnly(True)
        # 不再应用自定义样式，使用全局样式
        
        # 加载使用指南 HTML 内容
        guide_text.setHtml(self.load_guide_html())
        
        guide_layout.addWidget(guide_text)
    
    def load_guide_html(self):
        """加载使用指南 HTML 内容"""
        # 在实际应用中，可以从外部文件加载
        # 此处为简化示例，直接返回基本内容
        return """
        <style>
            h2 { color: #1976D2; margin-top: 20px; margin-bottom: 16px; }
            h3 { color: #2979FF; margin-top: 18px; margin-bottom: 12px; border-bottom: 1px solid #e0e0e0; padding-bottom: 8px; }
            h4 { color: #455A64; margin-top: 16px; margin-bottom: 8px; }
            p { text-align: justify; margin: 8px 0; line-height: 1.5; }
            ul, ol { margin-top: 8px; margin-bottom: 8px; }
            li { margin: 4px 0; line-height: 1.5; }
            b { color: #37474F; }
            .highlight { background-color: #FFF9C4; padding: 2px 4px; border-radius: 3px; }
            .note { background-color: #E3F2FD; padding: 12px; border-left: 4px solid #2196F3; margin: 12px 0; border-radius: 4px; }
            .warning { background-color: #FFF3E0; padding: 12px; border-left: 4px solid #FF9800; margin: 12px 0; border-radius: 4px; }
        </style>
        <h2>Micro Tracker 使用指南</h2>
        <div class="note" style="margin-bottom: 15px;">
            <h3 style="margin-top: 15px;">作者信息</h3>
            <p style="margin: 5px 0;">作者：LUCIEN</p>
            <p style="margin: 5px 0;">邮箱：lucien-6@qq.com</p>
            <p style="margin: 5px 0;">版本：1.2.1</p>
            <p style="margin: 5px 0;">发布日期：2025年5月27日</p>
            <p style="margin: 5px 0;">Copyright © 2025 LUCIEN. 保留所有权利。</p>
        </div>
        <p>Micro Tracker 是一个基于 SAM2 (Segment Anything Model 2) 的显微视频对象分割和跟踪工具。本工具采用最新的 SAM2 模型，可以帮助您对显微视频中的多个对象进行高精度自动分割和跟踪，广泛适用于视频分析、对象检测和视觉效果制作等场景。</p>
        
        <h3>基本使用流程：</h3>
        <ol>
            <li><b>选择视频文件：</b> 点击"浏览..."按钮选择要处理的视频文件。支持常见视频格式，如MP4、AVI、MOV和MKV等。</li>
            <li><b>确认模型路径：</b> 确保 SAM2 模型路径正确，默认为 models/sam2/checkpoints/sam2.1_hiera_tiny.pt。如需使用其他模型，可点击"浏览..."按钮选择模型文件。</li>
            <li><b>设置输出选项：</b> 指定输出视频路径和掩码保存目录（可选）。掩码目录用于保存对象分割的二进制掩码，便于后续处理和分析。</li>
            <li><b>标注初始边界框：</b> 在视频第一帧上，通过拖动鼠标绘制要跟踪对象的边界框。可以标注多个对象，系统会为每个对象分配唯一标识符。</li>
            <li><b>开始处理：</b> 点击"开始处理"按钮启动视频处理。处理过程中可以实时查看进度和预计完成时间。</li>
            <li><b>查看处理进度：</b> 在处理进度栏中查看实时处理日志，包括初始化信息、处理速度和预计剩余时间等。不同类型的信息以不同颜色显示，便于快速识别。</li>
            <li><b>查看结果：</b> 处理完成后自动切换到"结果预览"标签页查看处理结果。您可以播放、暂停并浏览处理后的视频，查看分割和跟踪效果。</li>
            <li><b>筛选数据：</b> 处理完成后，可以切换到"筛选过滤"标签页，对掩膜对象进行高级筛选、分析和数据导出。</li>
        </ol>
        
        <h3>界面功能详解：</h3>
        <h4>1. 参数设置与标注</h4>
        <ul>
            <li><b>文件选择区域：</b> 用于选择输入视频、模型文件、设置输出路径和掩码保存目录。</li>
            <li><b>参数设置区域：</b> 选择处理设备（CPU或GPU）和其他处理选项。</li>
            <li><b>视频预览区域：</b> 显示原始视频，并允许通过拖动鼠标绘制边界框标注要跟踪的对象。</li>
            <li><b>视频控制：</b> 
                <ul>
                    <li>播放/暂停按钮：控制视频播放状态</li>
                    <li>帧滑块：快速浏览视频的不同帧</li>
                    <li>清除边界框按钮：移除所有已标注的边界框</li>
                </ul>
            </li>
            <li><b>处理进度区域：</b> 显示处理日志和进度条，提供实时反馈。</li>
        </ul>
        
        <h4>2. 结果预览</h4>
        <ul>
            <li><b>结果视频预览：</b> 显示处理后的视频，包含分割掩码和对象边界框。</li>
            <li><b>视频控制：</b> 与参数设置页类似，但用于控制结果视频的播放和浏览。</li>
            <li><b>打开输出文件夹：</b> 直接访问输出视频所在的文件夹。</li>
        </ul>
        
        <h4>3. 筛选过滤</h4>
        <ul>
            <li><b>掩膜图片序列选择：</b> 选择包含掩膜图像的文件夹（通常是处理步骤自动生成的）。掩膜图像是8位灰度PNG图片，每个像素值表示对象ID，背景为0。</li>
            <li><b>参数设置：</b> 
                <ul>
                    <li>帧率 (FPS)：设置分析时的帧率，影响时间和速度计算</li>
                    <li>比例系数 (μm/pixel)：设置像素到实际物理尺寸的转换系数，影响尺寸和距离计算</li>
                </ul>
            </li>
            <li><b>筛选条件：</b> 可以设置六种不同的筛选条件
                <ul>
                    <li>面积区间：根据对象面积（μm²）筛选</li>
                    <li>面积变化率阈值：当相邻帧之间面积变化超过阈值时截断对象轨迹</li>
                    <li>瞬时速度区间：根据对象的瞬时移动速度（μm/s）筛选</li>
                    <li>总位移区间：根据对象从起点到终点的总位移（μm）筛选</li>
                    <li>边界截断排除：去除接触图像边界的对象部分</li>
                    <li>相互最短距离阈值：当两个对象距离小于阈值时截断轨迹</li>
                </ul>
            </li>
            <li><b>排除指定对象：</b> 可以手动输入要排除的对象ID（逗号分隔）</li>
            <li><b>筛选结果预览：</b> 显示筛选后的对象可视化，包括：
                <ul>
                    <li>彩色对象表示：每个对象赋予不同颜色</li>
                    <li>对象ID标签：清晰显示每个对象的唯一标识符</li>
                    <li>椭圆主轴和次轴：红色直线表示主轴（长轴），蓝色直线表示次轴（短轴）</li>
                    <li>对象轨迹：显示对象移动路径</li>
                </ul>
            </li>
            <li><b>统计信息：</b> 显示原始对象总数和通过筛选的对象数量</li>
            <li><b>筛选日志：</b> 详细记录筛选过程和每个对象的筛选结果及原因</li>
            <li><b>保存功能：</b> 将筛选结果保存为图像序列和数据表格（Excel/CSV）</li>
        </ul>
        
        <h4>4. 使用指南</h4>
        <ul>
            <li>提供详细的软件使用说明和功能介绍（当前页面）。</li>
        </ul>
        
        <h3>筛选过滤功能深度解析：</h3>
        <p>筛选过滤模块是本软件的关键高级功能，提供了对分割轨迹数据的深度分析和筛选能力。以下是详细的使用流程和功能解释：</p>
        
        <h4>1. 参数设置理解</h4>
        <ul>
            <li><b>帧率 (FPS)：</b> 定义每秒帧数，对计算对象速度和时间关系至关重要。例如，如果实际视频以1帧/秒拍摄，应设置为1.0；如果是每20秒一帧，则应设置为0.05。帧率调整会影响瞬时速度的计算，以及时间相关的数据分析。</li>
            <li><b>比例系数 (μm/pixel)：</b> 将像素单位转换为实际物理单位的系数。这个值应根据您的显微镜和摄像设置确定。例如，如果1个像素代表2.5微米，则设置为2.5。此系数会影响所有空间测量，包括面积、距离和速度。</li>
        </ul>
        
        <h4>2. 筛选条件详解</h4>
        <ul>
            <li><b>面积区间筛选：</b> 
                <ul>
                    <li>功能：筛选出面积在指定范围内的对象</li>
                    <li>单位：μm²（平方微米）</li>
                    <li>应用场景：去除过小的噪点或过大的聚合体/背景残留</li>
                    <li>工作原理：计算每个对象的像素面积，并乘以比例系数的平方转换为实际面积</li>
                </ul>
            </li>
            <li><b>面积变化率筛选：</b> 
                <ul>
                    <li>功能：当对象面积变化超过阈值时截断其轨迹</li>
                    <li>取值范围：0到1（比例值），表示小面积/大面积的比值</li>
                    <li>应用场景：检测对象融合、分裂或跟踪错误</li>
                    <li>工作原理：计算相邻帧之间面积比（较小值/较大值），低于阈值时判定为显著变化</li>
                </ul>
            </li>
            <li><b>瞬时速度区间：</b> 
                <ul>
                    <li>功能：根据对象的瞬时移动速度筛选</li>
                    <li>单位：μm/s（微米每秒）</li>
                    <li>应用场景：区分不同运动状态的对象，或识别跟踪跳变</li>
                    <li>工作原理：计算相邻帧之间质心位移除以时间间隔</li>
                </ul>
            </li>
            <li><b>总位移区间：</b> 
                <ul>
                    <li>功能：根据对象从起点到终点的直线距离筛选</li>
                    <li>单位：μm（微米）</li>
                    <li>应用场景：区分迁移和非迁移对象</li>
                    <li>工作原理：计算对象第一帧与最后一帧质心之间的直线距离</li>
                </ul>
            </li>
            <li><b>边界截断排除：</b> 
                <ul>
                    <li>功能：当对象接触图像边界时，截断其轨迹</li>
                    <li>应用场景：确保分析的是完整对象，避免部分截断的对象干扰分析</li>
                    <li>工作原理：检测掩膜像素是否接触图像四边</li>
                </ul>
            </li>
            <li><b>相互最短距离阈值：</b> 
                <ul>
                    <li>功能：当两个对象距离小于阈值时截断轨迹</li>
                    <li>单位：μm（微米）</li>
                    <li>应用场景：避免对象交互或拥挤状态的干扰</li>
                    <li>工作原理：计算对象轮廓间的最短距离，低于阈值时截断</li>
                </ul>
            </li>
        </ul>
        
        <h4>3. 筛选结果理解</h4>
        <ul>
            <li><b>完全通过：</b> 对象的整个轨迹都满足所有筛选条件</li>
            <li><b>部分截断：</b> 对象轨迹在某个时间点不满足条件，轨迹被截断但保留有效部分</li>
            <li><b>完全过滤：</b> 对象完全不满足筛选条件，或满足条件的帧数不足以形成有效轨迹</li>
        </ul>
        
        <h4>4. 可视化元素详解</h4>
        <ul>
            <li><b>彩色对象：</b> 每个对象以唯一颜色显示，便于区分</li>
            <li><b>对象ID：</b> 显示在对象中心，与处理阶段的ID一致</li>
            <li><b>椭圆主轴和次轴：</b> 对象经过椭圆拟合后的长轴（红色）和短轴（蓝色），用于分析对象形状和方向</li>
            <li><b>轨迹线：</b> 显示对象从出现到当前帧的移动路径</li>
        </ul>
        
        <h4>5. 数据保存与导出</h4>
        <p>点击"输出保存"按钮可以保存两类数据：</p>
        <ul>
            <li><b>筛选后的掩膜图像：</b> 保存为Filtered_Masks文件夹下的PNG序列，仅包含通过筛选的对象</li>
            <li><b>轨迹数据表格：</b> 保存为Excel（优先）或CSV格式，包含每个通过筛选的对象在各帧的详细属性数据：
                <ul>
                    <li>时间 (time)：以秒为单位</li>
                    <li>面积 (area)：以μm²为单位</li>
                    <li>质心坐标 (center_x, center_y)：以μm为单位</li>
                    <li>主轴长度 (major axis length)：椭圆长轴长度，以μm为单位</li>
                    <li>次轴长度 (minor axis length)：椭圆短轴长度，以μm为单位</li>
                    <li>姿态角度 (posture angle)：cv2.fitEllipse返回的原始角度值，表示椭圆方向，以度为单位</li>
                </ul>
            </li>
        </ul>
        
        <div class="note">
            <h4>关于姿态角度(posture angle)的理解：</h4>
            <p>导出的轨迹数据中的姿态角度是OpenCV的cv2.fitEllipse函数直接返回的原始角度值，表示椭圆的方向。这个角度测量的是椭圆宽度方向（可能是长轴或短轴）与水平线的夹角，范围为0-180度。</p>
            <p>注意：在可视化显示中，系统会自动确定哪个是主轴（长轴）并用红色显示，哪个是次轴（短轴）并用蓝色显示。但保存的角度数据始终是cv2.fitEllipse的原始返回值，没有经过调整。</p>
        </div>
        
        <h3>高级操作指南：</h3>
        
        <h4>边界框操作</h4>
        <ul>
            <li><b>绘制边界框：</b> 在视频画面上按住鼠标左键并拖动来绘制矩形边界框。</li>
            <li><b>选择边界框：</b> 点击已绘制的边界框可以选中它（边界框会以虚线显示）。</li>
            <li><b>删除边界框：</b> 选中边界框后按Delete键可以删除它。</li>
            <li><b>清除所有边界框：</b> 点击"清除边界框"按钮可以移除所有已绘制的边界框。</li>
        </ul>
        
        <h4>视频处理选项</h4>
        <ul>
            <li><b>处理设备选择：</b> 从下拉菜单中选择要使用的处理设备。推荐使用CUDA设备（GPU）以获得最佳性能。</li>
            <li><b>保存处理视频：</b> 选择是否将处理结果保存为视频文件。取消选中此选项可以只保存掩码而不生成视频。</li>
            <li><b>掩码保存：</b> 如果设置了掩码保存目录，系统会将每帧的分割掩码保存为单张8位灰度PNG图像，命名格式为"frame_yyyy.png"，其中yyyy是帧索引。在掩码中，不同对象用不同灰度值表示(对象ID+1)，背景为0值。这种统一格式减少了文件数量，便于后期处理和应用。</li>
        </ul>
        
        <h4>视频预览控制</h4>
        <ul>
            <li><b>播放/暂停：</b> 控制视频的播放和暂停。</li>
            <li><b>帧滑块：</b> 拖动滑块或点击滑块两侧的箭头可以精确导航到视频的特定帧。</li>
            <li><b>帧信息显示：</b> 显示当前帧号和总帧数。</li>
            <li><b>键盘快捷键 (聚焦视频控件时)：</b>
                <ul>
                    <li>空格键：播放/暂停</li>
                    <li>F 键 / 右方向键：下一帧</li>
                    <li>D 键 / 左方向键：上一帧</li>
                </ul>
            </li>
        </ul>
        
        <div class="warning">
            <h4>重要提示：</h4>
            <p>为了获得最佳性能和兼容性，请确保您的系统满足以下要求：</p>
            <ul>
                <li>操作系统：Windows 10/11, Linux, macOS</li>
                <li>Python版本：3.10+</li>
                <li>PyTorch版本：1.9.0 或更高版本 (CUDA版本视GPU而定)</li>
                <li>如果使用GPU加速，请确保已正确安装NVIDIA驱动和CUDA工具包</li>
            </ul>
            <p>如果遇到任何问题，请首先检查日志输出，并确保所有依赖项已正确安装。您可以通过邮件联系作者获取技术支持。</p>
        </div>
        
        <div class="note">\n            <p style="text-align: center; font-size: 9pt; color: #757575;">Micro Tracker v1.2.1 | Copyright © 2025 LUCIEN</p>\n        </div>
        """ 