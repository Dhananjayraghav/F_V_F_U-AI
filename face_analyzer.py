import cv2
import mediapipe as mp
import numpy as np

mp_face_detection = mp.solutions.face_detection


class FaceAnalyzer:
    def __init__(self):
        self.face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

    def analyze_face_tone(self, image, face_location):
        """Analyze the skin tone of the face"""
        x, y, w, h = face_location
        face_roi = image[y:y + h, x:x + w]

        # Convert to HSV color space for better skin tone analysis
        hsv = cv2.cvtColor(face_roi, cv2.COLOR_BGR2HSV)

        # Calculate average hue and saturation
        avg_hue = np.mean(hsv[:, :, 0])
        avg_sat = np.mean(hsv[:, :, 1])
        avg_val = np.mean(hsv[:, :, 2])

        # Classify skin tone based on HSV values
        if avg_val < 50:
            tone = "Very Dark"
        elif avg_val < 100:
            tone = "Dark"
        elif avg_hue < 10:
            tone = "Light with Warm Undertones"
        elif avg_hue < 20:
            tone = "Medium with Warm Undertones"
        elif avg_sat < 50:
            tone = "Light with Cool Undertones"
        else:
            tone = "Medium with Neutral Undertones"

        return tone, (int(avg_hue), int(avg_sat), int(avg_val))

    def process_frame(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(image_rgb)
        return results