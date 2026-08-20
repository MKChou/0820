"""CV demo: live camera. O = face, P = pose, G = gesture, Q/Esc = quit."""

from __future__ import annotations

import time
import urllib.request
from pathlib import Path

import cv2

try:
    import mediapipe as mp
    from mediapipe.tasks.python import vision
except ImportError:
    mp = None
    vision = None

HERE = Path(__file__).resolve().parent
MODEL_DIR = HERE / "models"

FACE_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_detector/blaze_face_short_range/float16/latest/"
    "blaze_face_short_range.tflite"
)
POSE_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "pose_landmarker/pose_landmarker_lite/float16/latest/"
    "pose_landmarker_lite.task"
)
GESTURE_MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "gesture_recognizer/gesture_recognizer/float16/latest/"
    "gesture_recognizer.task"
)

HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
)

POSE_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10), (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
    (11, 23), (12, 24), (23, 24), (23, 25), (25, 27), (27, 29), (27, 31),
    (24, 26), (26, 28), (28, 30), (28, 32),
)


def mediapipe_ready() -> bool:
    return mp is not None and vision is not None and hasattr(mp, "tasks")


def ensure_model(url: str, filename: str) -> Path:
    MODEL_DIR.mkdir(exist_ok=True)
    path = MODEL_DIR / filename
    if not path.exists():
        urllib.request.urlretrieve(url, path)
    return path


def open_camera() -> cv2.VideoCapture | None:
    for index in (0, 1, 2):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            return cap
        cap.release()
    return None


def draw_status(frame, face_on: bool, pose_on: bool, gesture_on: bool) -> None:
    lines = [
        "O: Face   P: Pose   G: Gesture   Q: Quit",
        f"Face: {'ON' if face_on else 'OFF'}",
        f"Pose: {'ON' if pose_on else 'OFF'}",
        f"Gesture: {'ON' if gesture_on else 'OFF'}",
    ]
    y = 28
    for line in lines:
        cv2.putText(
            frame,
            line,
            (12, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
            cv2.LINE_AA,
        )
        y += 28


def draw_faces(frame, result) -> None:
    h, w = frame.shape[:2]
    for detection in result.detections:
        box = detection.bounding_box
        x1 = max(0, box.origin_x)
        y1 = max(0, box.origin_y)
        x2 = min(w, box.origin_x + box.width)
        y2 = min(h, box.origin_y + box.height)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        for keypoint in detection.keypoints:
            cv2.circle(frame, (int(keypoint.x * w), int(keypoint.y * h)), 3, (0, 200, 255), -1)


def draw_pose(frame, landmarks) -> None:
    h, w = frame.shape[:2]
    points = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for i, j in POSE_CONNECTIONS:
        if i < len(points) and j < len(points):
            cv2.line(frame, points[i], points[j], (255, 0, 0), 2)
    for x, y in points:
        cv2.circle(frame, (x, y), 3, (0, 255, 255), -1)


def draw_gestures(frame, result) -> None:
    h, w = frame.shape[:2]
    hands = result.hand_landmarks or []
    gestures = result.gestures or []
    for index, landmarks in enumerate(hands):
        points = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
        for i, j in HAND_CONNECTIONS:
            if i < len(points) and j < len(points):
                cv2.line(frame, points[i], points[j], (0, 165, 255), 2)
        for x, y in points:
            cv2.circle(frame, (x, y), 3, (255, 255, 0), -1)

        label = "None"
        if index < len(gestures) and gestures[index]:
            label = gestures[index][0].category_name or "None"
        if points:
            cv2.putText(
                frame,
                label,
                (points[0][0] + 8, points[0][1] - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )


class Detectors:
    def __init__(self) -> None:
        self.face_on = False
        self.pose_on = False
        self.gesture_on = False
        self.face = None
        self.pose = None
        self.gesture = None
        self.start_ms = int(time.time() * 1000)

    def _timestamp_ms(self) -> int:
        return int(time.time() * 1000) - self.start_ms

    def toggle_face(self) -> None:
        if not mediapipe_ready():
            return
        self.face_on = not self.face_on
        if self.face_on and self.face is None:
            model_path = ensure_model(FACE_MODEL_URL, "blaze_face_short_range.tflite")
            options = vision.FaceDetectorOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
                running_mode=vision.RunningMode.VIDEO,
            )
            self.face = vision.FaceDetector.create_from_options(options)
        elif not self.face_on and self.face is not None:
            self.face.close()
            self.face = None

    def toggle_pose(self) -> None:
        if not mediapipe_ready():
            return
        self.pose_on = not self.pose_on
        if self.pose_on and self.pose is None:
            model_path = ensure_model(POSE_MODEL_URL, "pose_landmarker_lite.task")
            options = vision.PoseLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
                running_mode=vision.RunningMode.VIDEO,
            )
            self.pose = vision.PoseLandmarker.create_from_options(options)
        elif not self.pose_on and self.pose is not None:
            self.pose.close()
            self.pose = None

    def toggle_gesture(self) -> None:
        if not mediapipe_ready():
            return
        self.gesture_on = not self.gesture_on
        if self.gesture_on and self.gesture is None:
            model_path = ensure_model(GESTURE_MODEL_URL, "gesture_recognizer.task")
            options = vision.GestureRecognizerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
                running_mode=vision.RunningMode.VIDEO,
                num_hands=2,
            )
            self.gesture = vision.GestureRecognizer.create_from_options(options)
        elif not self.gesture_on and self.gesture is not None:
            self.gesture.close()
            self.gesture = None

    def apply(self, frame):
        if not self.face_on and not self.pose_on and not self.gesture_on:
            return frame

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = self._timestamp_ms()

        if self.face_on and self.face is not None:
            result = self.face.detect_for_video(mp_image, timestamp_ms)
            if result.detections:
                draw_faces(frame, result)

        if self.pose_on and self.pose is not None:
            result = self.pose.detect_for_video(mp_image, timestamp_ms)
            if result.pose_landmarks:
                draw_pose(frame, result.pose_landmarks[0])

        if self.gesture_on and self.gesture is not None:
            result = self.gesture.recognize_for_video(mp_image, timestamp_ms)
            if result.hand_landmarks:
                draw_gestures(frame, result)

        return frame

    def close(self) -> None:
        if self.face is not None:
            self.face.close()
            self.face = None
        if self.pose is not None:
            self.pose.close()
            self.pose = None
        if self.gesture is not None:
            self.gesture.close()
            self.gesture = None


def main() -> None:
    if not mediapipe_ready():
        print("Failed.")
        return

    cap = open_camera()
    if cap is None:
        print("Failed.")
        return

    detectors = Detectors()
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame = detectors.apply(frame)
            draw_status(frame, detectors.face_on, detectors.pose_on, detectors.gesture_on)
            cv2.imshow("Camera", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key in (ord("o"), ord("O")):
                detectors.toggle_face()
            elif key in (ord("p"), ord("P")):
                detectors.toggle_pose()
            elif key in (ord("g"), ord("G")):
                detectors.toggle_gesture()
    finally:
        detectors.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
