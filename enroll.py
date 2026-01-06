import cv2
import os
from ultralytics import YOLO

def enroll_face():
    #  YOLOv8 face detection model load gareko
    # yo model le frame ma face kata cha bhanera detect garcha
    model = YOLO('models/yolov8n-face.pt')
    
    name = input("Enter person's name: ").strip().replace(" ", "_")

    #  dataset bhitra tyo manche ko naam ko naya folder banayeko
    output_dir = os.path.join("dataset", name)
    os.makedirs(output_dir, exist_ok=True)
    # webcam start gareko (0 bhaneko primary camera ho)
    cap = cv2.VideoCapture(0)  
    count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        
# YOLO model use garera face detect gareko
        results = model(frame, verbose=False)
        boxes = results[0].boxes.xyxy.cpu().numpy()
     
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
# pura frame bata face matra cut-out (crop) gareko
# ROI (Region of Interest) 
            face = frame[y1:y2, x1:x2]
            count += 1
# Cropped face lai tyo manche ko folder ma save gareko
            cv2.imwrite(f"{output_dir}/{count}.jpg", face) 
# Screen ma face ko woripari green box banayeko
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
# १०. Live window dekhayeko        
        cv2.imshow("Enroll Face", frame)
# ११. Exit condition: 'q' thichema wa 20 ota photo save bhayema stop huncha
        if cv2.waitKey(1) == ord('q') or count >= 20:
            break
# १२. Camera banda gareko ra windows close gareko
    cap.release()
    cv2.destroyAllWindows()
    print(f"{name} enrolled with {count} images!")

if __name__ == "__main__":
    enroll_face()