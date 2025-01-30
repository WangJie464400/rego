from django.apps import AppConfig
from .yolov7.detect import YOLOv7Detector
from django.conf import settings

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # 初始化检测器
        self.detector = YOLOv7Detector(
            weights=settings.YOLOV7_WEIGHTS,
            device=settings.YOLOV7_DEVICE,
            img_size=settings.YOLOV7_IMG_SIZE,
            conf_thresh=settings.YOLOV7_CONF_THRESH,
            iou_thresh=settings.YOLOV7_IOU_THRESH,
            project=settings.YOLOV7_PROJECT,
            name=settings.YOLOV7_NAME,
            save_txt=False,
            save_img=True,
            view_img=False
        )
        print("YOLOv7 model loaded successfully.")