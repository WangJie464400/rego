# import torch
# import cv2
# from .models import FoodItem
# import numpy as np

# def load_model():
#     model = torch.hub.load('ultralytics/yolov7', 'custom', path='yolov7_food.pth')
#     return model

# def detect_food(image):
#     model = load_model()
#     img = cv2.imdecode(np.fromstring(image.read(), np.uint8), cv2.IMREAD_COLOR)
#     results = model(img)
#     detected_items = results.pandas().xyxy[0].to_dict(orient='records')
#     response = []
#     for item in detected_items:
#         food = FoodItem.objects.get(name=item['name'])
#         response.append({'name': food.name, 'calories': food.calories})
#     return response