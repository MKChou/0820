"""CV demo: live camera. O = face detection, P = pose detection, Q/Esc = quit."""

from __future__ import annotations

import cv2

try:
    import mediapipe as mp
except ImportError:
    mp = None


def open_camera() -> cv2.VideoCapture | None:
    for index in (0, 1, 2):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            return cap
        cap.release()
    return None


def draw_status(frame, face_on: bool, pose_on: bool) -> None:
    lines = [
        "O: Face   P: Pose   Q: Quit",
        f"Face: {'ON' if face_on else 'OFF'}",
        f"Pose: {'ON' if pose_on else 'OFF'}",
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


class Detectors:
    def __init__(self) -> None:
        self.face_on = False
        self.pose_on = False
        self.face = None
        self.pose = None
        self.mp_face = mp.solutions.face_detection if mp else None
        self.mp_pose = mp.solutions.pose if mp else None
        self.mp_draw = mp.solutions.drawing_utils if mp else None

    def toggle_face(self) -> None:
        if mp is None:
            return
        self.face_on = not self.face_on
        if self.face_on and self.face is None:
            self.face = self.mp_face.FaceDetection(
                model_selection=0,
                min_detection_confidence=0.5,
            )
        elif not self.face_on and self.face is not None:
            self.face.close()
            self.face = None

    def toggle_pose(self) -> None:
        if mp is None:
            return
        self.pose_on = not self.pose_on
        if self.pose_on and self.pose is None:
            self.pose = self.mp_pose.Pose(
                model_complexity=0,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
            )
        elif not self.pose_on and self.pose is not None:
            self.pose.close()
            self.pose = None

    def apply(self, frame):
        if not self.face_on and not self.pose_on:
            return frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        if self.face_on and self.face is not None:
            result = self.face.process(rgb)
            if result.detections:
                for detection in result.detections:
                    self.mp_draw.draw_detection(frame, detection)
        if self.pose_on and self.pose is not None:
            result = self.pose.process(rgb)
            if result.pose_landmarks:
                self.mp_draw.draw_landmarks(
                    frame,
                    result.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                )
        return frame

    def close(self) -> None:
        if self.face is not None:
            self.face.close()
            self.face = None
        if self.pose is not None:
            self.pose.close()
            self.pose = None


def main() -> None:
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
            draw_status(frame, detectors.face_on, detectors.pose_on)
            cv2.imshow("Camera", frame)

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key in (ord("o"), ord("O")):
                detectors.toggle_face()
            elif key in (ord("p"), ord("P")):
                detectors.toggle_pose()
    finally:
        detectors.close()
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
