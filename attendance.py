import cv2
import sqlite3
import pickle
import numpy as np
from datetime import datetime
from ultralytics import YOLO
import face_recognition
import os

# Yesma YOLO model ko 'nano' version (yolov8n) use bhako cha
model = YOLO('models/yolov8n-face.pt')

#Pailai train bhayera baseko face data (encodings) load gareko
with open('models/encodings.pkl', 'rb') as f:
    known_encodings, known_names = pickle.load(f)

# Attendance mark garne function
def mark_attendance(name, conn):
    today = datetime.now().strftime("%Y-%m-%d")
    time = datetime.now().strftime("%H:%M:%S")
    
    cursor = conn.cursor()
    
#Attendance pailai mark bhako cha ki chaina check gareko
# Eutai manche ko ek din ma ek choti matra attendance hosh bhannalaai yo check gareko ho
    cursor.execute("SELECT * FROM attendance WHERE name=? AND date=?", (name, today))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)", (name, today, time))
        conn.commit()
        print(f"✅ Attendance marked for {name}")
    cursor.close()

#  Database ma bhako attendance records herne function
def view_attendance(conn):
# Attendance table chaina bhane naya table create gareko
    cursor = conn.cursor()
    cursor.execute("SELECT name, date, time FROM attendance")
    records = cursor.fetchall()
    print("\n--- Attendance Records ---")
    for idx, (name, date, time) in enumerate(records, 1):
        print(f"{idx}. {name} | Date: {date} | Time: {time}")
    cursor.close()

def main():
    
    conn = sqlite3.connect('database/attendance.db')
    
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS attendance
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name TEXT,
                      date TEXT,
                      time TEXT)''')
    conn.commit()
    cursor.close()
    
    #Webcam start gareko
    cap = cv2.VideoCapture(0)
    print("Starting attendance system... (Press 'q' to quit)")
    
    while True:
        ret, frame =    cap.read()
        if not ret:
            break
        
#    YOLO use garera frame ma face detect gareko
        results = model(frame, verbose=False)
        boxes = results[0].boxes.xyxy.cpu().numpy()
        
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            face = frame[y1:y2, x1:x2]
            name = "Unknown"
            
#  Photo ko color BGR bata RGB ma convert gareko
# OpenCV le BGR use garcha tara face_recognition library lai RGB चाहिन्छ     
            rgb_face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
 #  Face encoding nikaleko           
            face_encodings = face_recognition.face_encodings(rgb_face)
            if face_encodings:
 #  Live face lai database ko known face sanga compare gareko               
                matches = face_recognition.compare_faces(known_encodings, face_encodings[0])
                face_distances = face_recognition.face_distance(known_encodings, face_encodings[0])
# Sabai bhanda dherai milne (minimum distance bhako) face chhaneko
                best_match_idx = np.argmin(face_distances)
                
                if matches[best_match_idx]:
                    name = known_names[best_match_idx]
                    mark_attendance(name, conn)
            
#  Screen ma box ra manche ko naam dekhayeko        
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, name, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        cv2.imshow("Attendance System", frame)
        if cv2.waitKey(1) == ord('q'):
            break
# Camara release garne ra database close garne
    cap.release()
    cv2.destroyAllWindows()
    print("\nAttendance system stopped.")
    
    
    choice = input("\nView attendance records? (y/n): ").lower()
    if choice == 'y':
        view_attendance(conn)
    
    conn.close()

if __name__ == "__main__":
    main()