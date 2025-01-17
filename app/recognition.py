# app/recognition.py
import numpy as np
from deepface import DeepFace
import cv2, time, os

THRESHOLD = 10.0  # Adjust as necessary

def recognize_face(face_roi, embeddings, labels, threshold=THRESHOLD):
    try:
        # Generate embedding for the face region
        result = DeepFace.represent(face_roi, model_name="Facenet", enforce_detection=False)
        face_embedding = result[0]["embedding"]
        print("[DEBUG] Generated face embedding.")

        if not embeddings:
            print("[DEBUG] No embeddings stored. Returning Unknown.")
            return "Unknown", None

        # Calculate Euclidean distances to stored embeddings
        distances = [np.linalg.norm(face_embedding - np.array(e)) for e in embeddings]
        min_dist = min(distances)
        min_idx = distances.index(min_dist)
        print(f"[DEBUG] Computed distances: {distances}, Min distance: {min_dist}")

        if min_dist < threshold:
            recognized_label = labels[min_idx]
            print(f"[INFO] Recognized face as '{recognized_label}' with distance {min_dist:.2f}")
            return recognized_label, min_dist
        else:
            print(f"[INFO] Face not recognized. Min distance {min_dist:.2f} exceeds threshold.")
            return "Unknown", min_dist
    except Exception as e:
        print(f"[ERROR] in recognize_face: {e}")
        return "Unknown", None

def add_new_person(face_roi, person_name, embeddings, labels):
    timestamp = int(time.time())
    folder = os.path.join("known_faces", person_name)
    os.makedirs(folder, exist_ok=True)
    face_path = os.path.join(folder, f"{person_name}_{timestamp}.jpg")
    cv2.imwrite(face_path, face_roi)

    try:
        result = DeepFace.represent(face_roi, model_name="Facenet", enforce_detection=False)
        new_embedding = result[0]["embedding"]
        embeddings.append(new_embedding)
        labels.append(person_name)
        print(f"[INFO] Added new embedding for {person_name}")
        return embeddings, labels
    except Exception as e:
        print(f"[ERROR] Could not generate embedding for {person_name}: {e}")
        return embeddings, labels
