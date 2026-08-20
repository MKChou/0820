"""CV demo: open the camera and show live video. Press q or Esc to quit."""

from __future__ import annotations

import cv2


def open_camera() -> cv2.VideoCapture | None:
    for index in (0, 1, 2):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            return cap
        cap.release()
    return None


def main() -> None:
    cap = open_camera()
    if cap is None:
        print("Failed.")
        return

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
