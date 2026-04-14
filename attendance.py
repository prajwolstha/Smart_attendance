import cv2
import sqlite3
import pickle
import numpy as np
from datetime import datetime
from ultralytics import YOLO
import face_recognition
import os

# --- INITIALIZATION ---
model = YOLO('models/yolov8n-face.pt')

try:
    with open('models/encodings.pkl', 'rb') as f:
        known_encodings, known_names = pickle.load(f)
except FileNotFoundError:
    print("Error: encodings.pkl not found. Run train.py first.")
    exit()

# Load Background (720x620 as per your measurements)
imgBackground = cv2.imread('assets/frame.png')

# Settings
CONFIRMATION_TIME = 4 

def mark_attendance(name, conn):
    today = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance WHERE name=? AND date=?", (name, today))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)", (name, today, time))
        conn.commit()
        print(f"✅ Attendance marked for {name}")
    cursor.close()

def main():
    os.makedirs('database', exist_ok=True)
    conn = sqlite3.connect('database/attendance.db')
    
    attendance_counters = {}
    cap = cv2.VideoCapture(0)
    
    # Standard webcam internal capture size
    cap.set(3, 640)
    cap.set(4, 480)

    print("System Running... Press 'q' to quit.")

    while True:
        success, img = cap.read()
        if not success:
            break

        # 1. AI Processing on raw camera 'img'
        results = model(img, verbose=False)
        boxes = results[0].boxes.xyxy.cpu().numpy()
        faces_in_frame = []

        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            face = img[y1:y2, x1:x2]
            name = "Unknown"
            
            if face.size > 0:
                rgb_face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
                face_encodings = face_recognition.face_encodings(rgb_face)
                
                if face_encodings:
                    matches = face_recognition.compare_faces(known_encodings, face_encodings[0])
                    face_distances = face_recognition.face_distance(known_encodings, face_encodings[0])
                    best_match_idx = np.argmin(face_distances)

                    if matches[best_match_idx]:
                        name = known_names[best_match_idx]
                        faces_in_frame.append(name)
                        
                        current_time = datetime.now()
                        if name not in attendance_counters:
                            attendance_counters[name] = current_time
                        else:
                            elapsed = (current_time - attendance_counters[name]).total_seconds()
                            progress = min(int((elapsed / CONFIRMATION_TIME) * 100), 100)
                            
                            # Progress Text
                            cv2.putText(img, f"{progress}%", (x1, y2 + 25), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                            
                            if elapsed >= CONFIRMATION_TIME:
                                mark_attendance(name, conn)
                                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 4)

            # Draw Label
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
            cv2.putText(img, name, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        # --- THE FIX: LAYERING & RESIZING ---
        # Create a fresh copy of the background
        display_img = imgBackground.copy()

        # Calculate width and height from your Paint points:
        # X: 1 to 720 (Width = 719)
        # Y: 84 to 550 (Height = 466)
        try:
            img_resized = cv2.resize(img, (719, 466))
            
            # Slicing: [y_start : y_end, x_start : x_end]
            display_img[84:550, 1:720] = img_resized
        except Exception as e:
            print(f"Layout Error: {e}. Check if frame.png is actually 720x620.")

        # Timer reset logic
        for person in list(attendance_counters.keys()):
            if person not in faces_in_frame:
                del attendance_counters[person]

        cv2.imshow("Smart Attendance System", display_img)
        
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    conn.close()

if __name__ == "__main__":
    main()