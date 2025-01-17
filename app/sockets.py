import base64
import io
import time  # Import time for timing logs
from PIL import Image
import numpy as np
import cv2
from ultralytics import YOLO
from deepface import DeepFace
from .recognition import recognize_face, add_new_person

# Global YOLO model; ensure that "yolo_face_detection_S.pt" is in your project root.
model = YOLO("yolo_face_detection_S.pt")

# Global in-memory embeddings (for demo purposes)
known_embeddings = []
known_labels = []

def handle_frame(data):
    start_time = time.time()
    try:
        # Decode the received data URL to obtain the image
        _, encoded = data.split(',', 1)
        decoded = base64.b64decode(encoded)
        img_pil = Image.open(io.BytesIO(decoded))
        frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

        # Run YOLO detection and time this step
        detection_start = time.time()
        results = model(frame, verbose=False)
        detection_end = time.time()
        print("[DEBUG] YOLO detection time:", detection_end - detection_start, "seconds")

        # Extract bounding boxes; convert them to numpy array if needed
        bboxes = results[0].boxes.xyxy
        if hasattr(bboxes, "cpu"):
            bboxes = bboxes.cpu().numpy()

        print("[DEBUG] Detected faces:", len(bboxes))

        # Draw bounding boxes on the frame
        for bbox in bboxes:
            x1, y1, x2, y2 = map(int, bbox[:4])
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(x2, frame.shape[1] - 1), min(y2, frame.shape[0] - 1)
            face_roi = frame[y1:y2, x1:x2]
            if face_roi.size == 0:
                continue

            # Call recognition function to get the label and distance
            label, dist = recognize_face(face_roi, known_embeddings, known_labels)
            if label is None or label == "":
                label = "Unknown"

            # Prepare text label: include distance if available
            text_label = label if dist is None else f"{label} ({dist:.2f})"
            
            # Choose rectangle color: green for recognized, red for unknown
            color_box = (0, 255, 0) if label != "Unknown" else (0, 0, 255)
            
            # Draw rectangle and overlay text
            cv2.rectangle(frame, (x1, y1), (x2, y2), color_box, 2)
            cv2.putText(frame, text_label, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # Encode the annotated frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')

        total_time = time.time() - start_time
        print("[DEBUG] Total processing time:", total_time, "seconds")
        return f"data:image/jpeg;base64,{jpg_as_text}"
    except Exception as e:
        print(f"[ERROR] handle_frame: {e}")
        return None

def handle_tag(data):
    try:
        face_data = data.get('face_image')
        person_name = data.get('name')
        if not face_data or not person_name:
            return {"status": "failure", "message": "Invalid data for tagging."}
        
        _, encoded = face_data.split(',', 1)
        decoded = base64.b64decode(encoded)
        img_pil = Image.open(io.BytesIO(decoded))
        face_roi = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        
        # Add a new embedding (for demonstration, we're storing a real embedding in production you'd use DeepFace.represent)
        add_new_person(face_roi, person_name, known_embeddings, known_labels)
        print(f"[INFO] Added new embedding for {person_name}")
        return {"status": "success", "message": f"{person_name} added successfully."}
    except Exception as e:
        print(f"[ERROR] handle_tag: {e}")
        return {"status": "failure", "message": "An error occurred during tagging."}
