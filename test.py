import cv2
from ultralytics import YOLO

model = YOLO('models/yolov8n-face.pt')
cap=cv2.VideoCapture(0)