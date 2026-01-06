import os
import face_recognition
import pickle

def train_faces():
#  Dataset ko photos haru lai mathematical data (encodings) ma badalne function
    known_encodings = []
    known_names = []
#  'dataset' folder bhitra bhayeka sabai student ko folders haru scan gareko  
    for person in os.listdir("dataset"):
        person_dir = os.path.join("dataset", person)
#  Yadi tyo directory ho bhane matra bhitra ko images haru herne
        if os.path.isdir(person_dir):
            for img_file in os.listdir(person_dir):
                img_path = os.path.join(person_dir, img_file)
# 4. Photo lai face_recognition library use garera load gareko
                image = face_recognition.load_image_file(img_path)
# 5. Face ko unique features nikaleko (Yeslai 128-dimensional encoding bhannincha)

                encoding = face_recognition.face_encodings(image)
# 6. Yadi photo ma face bhetiyo bhane matra list ma store garne
                if encoding:
                    known_encodings.append(encoding[0])
                    known_names.append(person)

    # Save encodings
    with open("models/encodings.pkl", "wb") as f:
        pickle.dump((known_encodings, known_names), f)
    print(f"Trained {len(known_names)} faces!")

if __name__ == "__main__":
    train_faces()