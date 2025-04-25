import mediapipe as mp
import numpy as np
from enum import Enum
from typing import Dict, Tuple, List

mp_pose = mp.solutions.pose


class PostureType(Enum):
    NEUTRAL = 0
    KYPHOTIC = 1  # Hunched back
    LORDOTIC = 2  # Sway back
    SWAY_BACK = 3
    FORWARD_HEAD = 4


class ShoulderAlignment(Enum):
    EVEN = 0
    LEFT_HIGH = 1
    RIGHT_HIGH = 2


def is_full_body(landmarks) -> bool:
    """Enhanced full-body detection with confidence scoring"""
    required_landmarks = [
        (mp_pose.PoseLandmark.LEFT_SHOULDER, 0.7),
        (mp_pose.PoseLandmark.RIGHT_SHOULDER, 0.7),
        (mp_pose.PoseLandmark.LEFT_HIP, 0.7),
        (mp_pose.PoseLandmark.RIGHT_HIP, 0.7),
        (mp_pose.PoseLandmark.LEFT_KNEE, 0.5),
        (mp_pose.PoseLandmark.RIGHT_KNEE, 0.5)
    ]

    visibility_score = sum(landmarks[lm].visibility for lm, _ in required_landmarks)
    return visibility_score >= sum(thresh for _, thresh in required_landmarks)


def get_body_measurements(landmarks, image_shape: Tuple[int, int], pixel_to_cm_ratio: float) -> Dict:
    """Enhanced measurements with posture analysis"""
    height, width = image_shape[:2]
    measurements = {}

    # Basic measurements (existing)
    measurements.update(_get_basic_measurements(landmarks, height, width, pixel_to_cm_ratio))

    # Advanced posture metrics (new)
    posture_metrics = analyze_posture(landmarks, height, width)
    measurements.update(posture_metrics)

    # Body proportions (new)
    proportions = calculate_proportions(measurements)
    measurements.update(proportions)

    # Movement potential (new)
    flexibility = estimate_flexibility(landmarks, height, width)
    measurements.update(flexibility)

    return measurements


def _get_basic_measurements(landmarks, height: int, width: int, ratio: float) -> Dict:
    """Your existing measurement calculations"""
    measurements = {}

    # Shoulder width
    measurements['shoulder_width'] = abs(
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x -
        landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x
    ) * width * ratio

    # Chest circumference (improved approximation)
    shoulder_to_shoulder = measurements['shoulder_width']
    chest_depth = abs(
        landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y -
        landmarks[mp_pose.PoseLandmark.LEFT_HIP].y
    ) * height * ratio * 0.6
    measurements['chest'] = (shoulder_to_shoulder * 2) + (chest_depth * 2)

    # Arm length (improved 3D approximation)
    measurements['left_arm'] = calculate_3d_length(
        landmarks,
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.LEFT_ELBOW,
        mp_pose.PoseLandmark.LEFT_WRIST,
        height, width, ratio
    )

    # ... (other basic measurements)

    return measurements


def analyze_posture(landmarks, height: int, width: int) -> Dict:
    """Comprehensive posture analysis"""
    posture = {}

    # 1. Shoulder Alignment
    left_y = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].y * height
    right_y = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].y * height
    slope_deg = np.degrees(np.arctan2(right_y - left_y, width * 0.2))  # Normalized

    if abs(slope_deg) > 5:
        posture['shoulder_alignment'] = ShoulderAlignment.LEFT_HIGH if slope_deg > 0 else ShoulderAlignment.RIGHT_HIGH
        posture['shoulder_slope_deg'] = slope_deg
    else:
        posture['shoulder_alignment'] = ShoulderAlignment.EVEN

    # 2. Spinal Curvature
    neck = (landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER].x + landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER].x) / 2
    mid_back = (landmarks[mp_pose.PoseLandmark.LEFT_HIP].x + landmarks[mp_pose.PoseLandmark.RIGHT_HIP].x) / 2
    curvature = abs(neck - mid_back) * width

    if curvature > 0.15 * width:  # 15% of image width
        posture['posture_type'] = PostureType.KYPHOTIC if curvature > 0 else PostureType.LORDOTIC
    else:
        posture['posture_type'] = PostureType.NEUTRAL

    # 3. Forward Head
    nose_y = landmarks[mp_pose.PoseLandmark.NOSE].y * height
    shoulder_y = (left_y + right_y) / 2
    posture['head_forward_ratio'] = (shoulder_y - nose_y) / height

    return posture


def calculate_proportions(measurements: Dict) -> Dict:
    """Calculate body proportions for fashion recommendations"""
    proportions = {}

    # Torso-to-leg ratio
    torso_length = measurements['chest'] / 2.5  # Approximation
    leg_length = (measurements['left_leg'] + measurements['right_leg']) / 2
    proportions['torso_leg_ratio'] = torso_length / leg_length

    # Shoulder-to-hip ratio
    shoulder_width = measurements['shoulder_width']
    hip_width = measurements['waist'] / 2.2  # Reverse calculation
    proportions['shoulder_hip_ratio'] = shoulder_width / hip_width

    # Body type classification
    if proportions['shoulder_hip_ratio'] > 1.05:
        proportions['body_type'] = 'inverted_triangle'
    elif proportions['shoulder_hip_ratio'] < 0.95:
        proportions['body_type'] = 'pear'
    else:
        proportions['body_type'] = 'balanced'

    return proportions


def estimate_flexibility(landmarks, height: int, width: int) -> Dict:
    """Estimate body flexibility based on joint angles"""
    flexibility = {}

    # Shoulder mobility
    shoulder_angle = calculate_joint_angle(
        landmarks,
        mp_pose.PoseLandmark.LEFT_ELBOW,
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.LEFT_HIP,
        height, width
    )
    flexibility['shoulder_flexibility'] = min(100, max(0, (shoulder_angle - 45) / 1.2))  # Scale 0-100

    # Hip flexibility
    hip_angle = calculate_joint_angle(
        landmarks,
        mp_pose.PoseLandmark.LEFT_SHOULDER,
        mp_pose.PoseLandmark.LEFT_HIP,
        mp_pose.PoseLandmark.LEFT_KNEE,
        height, width
    )
    flexibility['hip_flexibility'] = min(100, max(0, (hip_angle - 160) / 0.4))

    return flexibility


def calculate_joint_angle(landmarks, a: int, b: int, c: int, height: int, width: int) -> float:
    """Calculate joint angle between three landmarks"""
    # Convert landmarks to image coordinates
    a_point = np.array([landmarks[a].x * width, landmarks[a].y * height])
    b_point = np.array([landmarks[b].x * width, landmarks[b].y * height])
    c_point = np.array([landmarks[c].x * width, landmarks[c].y * height])

    # Calculate vectors
    ba = a_point - b_point
    bc = c_point - b_point

    # Calculate angle
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(cosine_angle))


def calculate_3d_length(landmarks, start: int, mid: int, end: int, height: int, width: int, ratio: float) -> float:
    """Calculate 3D length through multiple joints"""
    # Convert to 3D space (using relative z from MediaPipe)
    start_pt = np.array([
        landmarks[start].x * width,
        landmarks[start].y * height,
        landmarks[start].z * width  # Approximate depth
    ])
    mid_pt = np.array([
        landmarks[mid].x * width,
        landmarks[mid].y * height,
        landmarks[mid].z * width
    ])
    end_pt = np.array([
        landmarks[end].x * width,
        landmarks[end].y * height,
        landmarks[end].z * width
    ])

    # Sum segment lengths
    length = (np.linalg.norm(start_pt - mid_pt) + np.linalg.norm(mid_pt - end_pt))
    return length * ratio