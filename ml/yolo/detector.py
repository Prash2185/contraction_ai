# ml/yolo/detector.py
"""
YOLOv8 Detector — Construction Site Object Detection
Detects: Pillar, Beam, Column, Wall, Slab
"""

import cv2
import numpy as np
from typing import List, Tuple
import os

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("WARNING: ultralytics not installed. Using mock detector.")


CONSTRUCTION_CLASSES = ["Pillar", "Beam", "Column", "Wall", "Slab", "Footing"]

# Pixel to inch conversion (calibrate per site)
# Assumes 1 pixel = 0.166 inches at standard drone height
PIXEL_TO_INCH = 0.166


class ConstructionDetector:
    def __init__(self, model_path: str = None):
        self.model = None
        self.model_path = model_path or os.getenv("YOLO_MODEL_PATH", "ml/yolo/construction_model.pt")
        self.confidence_threshold = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))

        if YOLO_AVAILABLE and os.path.exists(self.model_path):
            self.model = YOLO(self.model_path)
            print(f"✅ YOLOv8 model loaded: {self.model_path}")
        else:
            print("⚠️  YOLOv8 model not found — using mock detections for demo.")

    def preprocess(self, image_bytes: bytes) -> np.ndarray:
        """
        Phase 2 — OpenCV preprocessing:
        1. Decode image bytes to numpy matrix
        2. Resize to standard 640x640 (YOLO input)
        3. Denoise
        4. Normalize
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Could not decode image. Check format (JPG/PNG).")

        # Step 1: Resize to 640x640 for YOLO
        img_resized = cv2.resize(img, (640, 640))

        # Step 2: Denoise (reduces camera/drone noise)
        img_denoised = cv2.fastNlMeansDenoisingColored(img_resized, None, 10, 10, 7, 21)

        # Step 3: Enhance contrast using CLAHE
        lab = cv2.cvtColor(img_denoised, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l = clahe.apply(l)
        img_enhanced = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)

        return img_enhanced

    def detect(self, image_bytes: bytes) -> List[dict]:
        """
        Run YOLOv8 inference on preprocessed image.
        Returns list of detections with bounding boxes + coordinates.
        """
        img = self.preprocess(image_bytes)

        if self.model is not None:
            # Real YOLOv8 inference
            results = self.model(img, conf=self.confidence_threshold)
            detections = []
            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2
                    detections.append({
                        "object_type": CONSTRUCTION_CLASSES[cls_id] if cls_id < len(CONSTRUCTION_CLASSES) else f"Class_{cls_id}",
                        "confidence": round(float(box.conf[0]), 3),
                        "detected_x": cx,
                        "detected_y": cy,
                        "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                        "bbox_width": x2 - x1,
                        "bbox_height": y2 - y1,
                    })
            return detections
        else:
            # Mock detection for demo (no model file needed)
            return self._mock_detect()

    def _mock_detect(self) -> List[dict]:
        """Demo detections when no model is trained yet"""
        import random
        mocks = []
        for i, obj_type in enumerate(["Pillar", "Beam", "Column"]):
            base_x = 150 + i * 170
            base_y = 300 + random.randint(-20, 20)
            mocks.append({
                "object_type": obj_type,
                "confidence": round(0.85 + random.random() * 0.12, 3),
                "detected_x": base_x,
                "detected_y": base_y,
                "bbox": {"x1": base_x-40, "y1": base_y-60, "x2": base_x+40, "y2": base_y+60},
                "bbox_width": 80,
                "bbox_height": 120,
            })
        return mocks

    def compare_with_cad(self, detections: List[dict], cad_coords: List[dict]) -> List[dict]:
        """
        Compare YOLO detections with CAD reference coordinates.
        Returns mismatches with delta values and physical offset in inches.
        """
        results = []
        ERROR_THRESHOLD_PX = 20  # pixels — tune per site scale

        for detection in detections:
            # Find matching CAD element by type
            cad_match = next(
                (c for c in cad_coords if c["object_type"].lower() == detection["object_type"].lower()),
                None
            )
            if not cad_match:
                continue

            delta_x = detection["detected_x"] - cad_match["x"]
            delta_y = detection["detected_y"] - cad_match["y"]
            offset_px = (delta_x**2 + delta_y**2) ** 0.5
            offset_inches = round(offset_px * PIXEL_TO_INCH, 2)
            is_error = offset_px > ERROR_THRESHOLD_PX

            results.append({
                "object_type": detection["object_type"],
                "confidence": detection["confidence"],
                "detected_x": detection["detected_x"],
                "detected_y": detection["detected_y"],
                "expected_x": cad_match["x"],
                "expected_y": cad_match["y"],
                "delta_x": delta_x,
                "delta_y": delta_y,
                "offset_inches": offset_inches,
                "is_error": is_error,
                "bbox": detection.get("bbox"),
            })

        return results

    def draw_detections(self, image_bytes: bytes, mismatches: List[dict]) -> bytes:
        """
        Draw bounding boxes on image:
        - RED box = mismatched (error)
        - GREEN box = correctly placed
        Returns annotated image as bytes.
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img = cv2.resize(img, (640, 640))

        for m in mismatches:
            bbox = m.get("bbox")
            if not bbox:
                cx, cy = m["detected_x"], m["detected_y"]
                bbox = {"x1": cx-40, "y1": cy-60, "x2": cx+40, "y2": cy+60}

            color = (0, 0, 255) if m["is_error"] else (0, 255, 0)  # BGR
            cv2.rectangle(img, (bbox["x1"], bbox["y1"]), (bbox["x2"], bbox["y2"]), color, 2)

            label = f"{m['object_type']} {m['confidence']*100:.0f}%"
            if m["is_error"]:
                label += f" | ERR +{m['offset_inches']}in"

            cv2.putText(img, label, (bbox["x1"], bbox["y1"] - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1, cv2.LINE_AA)

            # Draw expected position as blue cross
            ex, ey = m["expected_x"], m["expected_y"]
            cv2.drawMarker(img, (ex, ey), (255, 150, 0), cv2.MARKER_CROSS, 20, 2)

        _, buf = cv2.imencode(".jpg", img)
        return buf.tobytes()
