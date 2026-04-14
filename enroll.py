import cv2
import os
import sys
from ultralytics import YOLO

def enroll_face(name_from_gui=None):
    # YOLO model load gareko
    model = YOLO('models/yolov8n-face.pt')
    
    # Check garne: Streamlit bata nam aako cha ki nai
    if name_from_gui:
        name = name_from_gui
    else:
        # User le manually script run garema matra terminal ma sodhcha
        name = input("Enter person's name: ").strip().replace(" ", "_")
        
    output_dir = "dataset/all_faces"
    os.makedirs(output_dir, exist_ok=True)
    
    # Laptop camera (0) open gareko
    cap = cv2.VideoCapture(0)  
    count = 0
    
    if not cap.isOpened():
        print("Error: Camera khulena!")
        return

    print(f"Starting enrollment for {name}. Photo khichdai cha...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Face detect gareko
        results = model(frame, verbose=False)
        boxes = results[0].boxes.xyxy.cpu().numpy()
     
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            face = frame[y1:y2, x1:x2]
            
            if face.size > 0:
                count += 1
                # Filename logic: Name_Number.jpg
                file_path = f"{output_dir}/{name}_{count}.jpg"
                cv2.imwrite(file_path, face) 
                
                # Screen ma feedback dekhayeko
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"Captured: {count}/20", (x1, y1-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("Enroll Face - All in One Folder", frame)
        
        # 20 photo bhayepachi aafai banda huncha
        if cv2.waitKey(1) == ord('q') or count >= 20:
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"✅ Success! 20 images of {name} saved.")

if __name__ == "__main__":
    # System arguments check gareko (Streamlit le pathauda index 1 ma name huncha)
    if len(sys.argv) > 1:
        enroll_face(sys.argv[1])
    else:
        enroll_face()