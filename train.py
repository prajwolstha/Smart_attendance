import cv2
import face_recognition
import pickle
import os

def generate_encodings():
    # Sabai photo bhayeko common folder path
    dataset_path = "dataset/all_faces"
    models_dir = "models"
    os.makedirs(models_dir, exist_ok=True)
    
    known_encodings = []
    known_names = []

    print("--- Encoding Process Start bhayo ---")

    # Folder bhitra bhayeka sabai images check gareko
    if not os.path.exists(dataset_path):
        print(f"Error: {dataset_path} folder vetiyena!")
        return

    for image_name in os.listdir(dataset_path):
        if image_name.endswith((".jpg", ".png", ".jpeg")):
            # Filename bata name matra nikaleko 
            # "pranju_shrestha_1.jpg" lai "_" ma split garera "pranju_shrestha" liyeko
            person_name = image_name.rsplit('_', 1)[0]
            
            image_path = os.path.join(dataset_path, image_name)
            image = cv2.imread(image_path)
            
            if image is None:
                continue
                
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Face encoding nikaleko
            # HOG model fast huncha, accurate ko lagi 'cnn' use garna sakincha
            boxes = face_recognition.face_locations(rgb_image, model='hog')
            encodings = face_recognition.face_encodings(rgb_image, boxes)

            if encodings:
                known_encodings.append(encodings[0])
                known_names.append(person_name)
                print(f"Success: {image_name} encoded for {person_name}")

    # Data lai .pkl file ma save gareko
    with open('models/encodings.pkl', 'wb') as f:
        pickle.dump((known_encodings, known_names), f)
    
    print("✅ Encodings saved! Aba attendance.py run garna tayar cha.")

if __name__ == "__main__":
    generate_encodings()