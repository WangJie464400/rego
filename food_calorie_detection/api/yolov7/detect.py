import subprocess
import torch
import random
import numpy as np
import cv2
import os
import sys
from pathlib import Path
from .utils.general import non_max_suppression
from .utils.datasets import LoadStreams, LoadImages
from .utils.general import (
    check_img_size, non_max_suppression, scale_coords,
    set_logging, select_device
)
from .utils.plots import plot_one_box
import ffmpeg
from tqdm import tqdm
import logging  # 引入 logging 模块

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

BASE_DIR = Path(__file__).resolve().parent.parent

class YOLOv7Detector:
    def __init__(self, weights, device='0', img_size=640, conf_thresh=0.25, iou_thresh=0.45,
                 project=f'{BASE_DIR}/results', name='exp', save_txt=False, save_img=True, view_img=False):
        self.weights = weights
        self.device = select_device(device)
        self.half = self.device.type != 'cpu'
        self.img_size = img_size
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh
        self.project = Path(project)
        self.name = name
        self.save_txt = save_txt
        self.save_img = save_img
        self.view_img = view_img
        self.frame_counter = 0  # 初始化帧计数器

        # 初始化
        set_logging()  # 启用日志记录
        self.logger = logging.getLogger(__name__)  # 获取日志记录器
        self.model = torch.load(self.weights, map_location=self.device, weights_only=False)['model'].float()
        self.model.to(self.device)
        if self.half:
            self.model.half()
        
        self.model.eval()

        # 获取模型信息
        stride = int(self.model.stride.max())
        self.img_size = check_img_size(self.img_size, s=stride)
        
        # 创建保存目录
        self.save_dir = self.project / self.name
        self.save_dir.mkdir(parents=True, exist_ok=True)

        # 初始化检测结果存储
        self.detected_items = []
        self.current_id = 1  # 用于分配唯一ID

    def detect(self, source):
        webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
            ('rtsp://', 'rtmp://', 'http://', 'https://'))
        
        # 设置数据加载器
        if webcam:
            dataset = LoadStreams(source, img_size=self.img_size, stride=int(self.model.stride.max()))
        else:
            dataset = LoadImages(source, img_size=self.img_size, stride=int(self.model.stride.max()))
        
        # 检查是否处理的是视频文件
        if len(dataset.files) == 1 and dataset.video_flag[0]:
            total_frames = dataset.nframes  # 设置为视频的实际帧数
        else:
            total_frames = len(dataset.files)  # 处理单张图片或多个图片
        self.logger.info(f"Total frames: {total_frames}")  # 使用日志记录

        # 类别和颜色
        names = self.model.names
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]

        # 初始化 FFmpeg 进程
        process = None
        frame_rate = 30
        frame_width = self.img_size
        frame_height = self.img_size

        # 初始化进度条
        progress_bar = tqdm(total=total_frames, desc='Processing Frames', unit='frame', ncols=100)

        for path, img, im0s, vid_cap in dataset:
            if process is None and self.save_img and not webcam and Path(source).suffix.lower() in ['.mp4', '.avi', '.mov']:
                save_path = str(self.save_dir / f"{Path(source).stem}.mp4")
                
                if vid_cap:
                    frame_rate = vid_cap.get(cv2.CAP_PROP_FPS)
                    frame_width = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    frame_height = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                else:
                    # 如果无法获取vid_cap信息，使用默认值
                    frame_rate = 30
                    frame_width, frame_height = self.img_size, self.img_size

                process = (
                    ffmpeg
                    .input(
                        'pipe:',
                        format='rawvideo',
                        pix_fmt='bgr24',  # 使用 BGR 格式
                        s='{}x{}'.format(frame_width, frame_height),
                        framerate=frame_rate
                    )
                    .output(save_path, pix_fmt='yuv420p', vcodec='libx264')  # 确保覆盖输出
                    .overwrite_output()  # 再次确保覆盖
                    .global_args('-loglevel', 'error')
                   .run_async(pipe_stdin=True, pipe_stdout=subprocess.DEVNULL, pipe_stderr=subprocess.DEVNULL)  # 重定向 stdout 和 stderr
                )

            with torch.no_grad():
                img = torch.from_numpy(img).to(self.device)
                img = img.half() if self.half else img.float()
                img /= 255.0
                if img.ndimension() == 3:
                    img = img.unsqueeze(0)

                # 推理
                pred = self.model(img, augment=False)[0]

                # 应用NMS
                pred = non_max_suppression(pred, self.conf_thresh, self.iou_thresh, classes=None, agnostic=False)

            # 处理检测结果
            for i, det in enumerate(pred):
                if webcam:
                    p, s, im0 = path[i], '', im0s[i].copy()
                else:
                    p, s, im0 = path, '', im0s

                p = Path(p)

                if len(det):
                    det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                    for *xyxy, conf, cls in reversed(det):
                        label = f'{names[int(cls)]} {conf:.2f}'
                        plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=2)
    
                        # 在边界框右上角框外绘制ID
                        x1, y1, x2, y2 = map(int, xyxy)
                        id_label = f'ID:{self.current_id}'
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        font_scale = 0.5
                        thickness = 1
                        text_size, _ = cv2.getTextSize(id_label, font, font_scale, thickness)
                        text_width, text_height = text_size

                        # 设置文本位置在边界框的右上角框外
                        text_x = x2 - text_width - 5  # 距离右边框5个像素
                        text_y = y1 - 5  # 位于框外，距离上边框5个像素

                        # 如果文本超出图片顶部，调整位置到框内
                        if text_y - text_height < 0:
                            text_y = y1 + text_height + 5

                        # 绘制背景矩形
                        cv2.rectangle(
                            im0, 
                            (text_x, text_y - text_height - 2), 
                            (text_x + text_width + 2, text_y + 2), 
                            colors[int(cls)], 
                            thickness=cv2.FILLED
                        )

                        # 绘制文本
                        cv2.putText(
                            im0, 
                            id_label, 
                            (text_x, text_y), 
                            font, 
                            font_scale, 
                            (255, 255, 255), 
                            thickness, 
                            cv2.LINE_AA
                        )

                        # 添加检测结果到 detected_items
                        self.detected_items.append({
                            'id': self.current_id,
                            'class_name': names[int(cls)],
                            'confidence': float(conf),
                            'bbox': [x1, y1, x2, y2]  # 包括边界框坐标
                        })
                        self.current_id += 1

                # 使用 FFmpeg 保存图像
                if self.save_img:
                    if not webcam and Path(source).suffix.lower() in ['.mp4', '.avi', '.mov'] and process is not None:
                        # 确保帧尺寸一致
                        frame_height_current, frame_width_current = im0.shape[:2]
                        if (frame_width_current != frame_width) or (frame_height_current != frame_height):
                            im0 = cv2.resize(im0, (frame_width, frame_height))

                        # 使用 BGR 格式
                        im0_bgr = im0

                        # 验证帧数据
                        assert im0_bgr.shape == (frame_height, frame_width, 3), f"Unexpected frame shape: {im0_bgr.shape}"
                        assert im0_bgr.dtype == np.uint8, f"Unexpected frame dtype: {im0_bgr.dtype}"

                        try:
                            process.stdin.write(im0_bgr.tobytes())
                        except BrokenPipeError:
                            break
                        except Exception as e:
                            break
                    else:
                        unique_filename = f"{Path(p.stem).name}.jpg"
                        save_path_img = str(self.save_dir / unique_filename)
                        cv2.imwrite(save_path_img, im0)
                        self.frame_counter += 1  # 更新帧计数器

            # 更新进度条
            progress_bar.update(1)

            # 清除 CUDA 缓存
            torch.cuda.empty_cache()

        # 释放进度条
        progress_bar.close()

        # 释放 FFmpeg 进程
        if self.save_img and process is not None:
            process.stdin.close()
            process.wait()

        self.logger.info(f'Detection complete! Results saved to {self.save_dir}')