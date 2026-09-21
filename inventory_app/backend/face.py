"""Face gate: landmarks, oval-region check, and background-free face crops.

Uses OpenCV YuNet so the app does not depend on MediaPipe / TensorFlow.
"""

from __future__ import annotations

import os
import urllib.request

import cv2
import numpy as np

from config import BASE_DIR

YUNET_URLS = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
    "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx",
)
YUNET_PATH = os.path.join(BASE_DIR, "models", "face_detection_yunet_2023mar.onnx")

# Must match dashboard GATE_OVAL / face silhouette (normalized 0-1).
OVAL_CX = 0.50
OVAL_CY = 0.50
OVAL_RX = 0.115
OVAL_RY = 0.195
# Face center must sit inside this fraction of the oval (middle of the section).
CENTER_FRAC = 0.55

IN_REGION_RATIO = 0.50
MIN_FACE_WIDTH = 0.07
MIN_FACE_HEIGHT = 0.10
MIN_EYE_DIST = 0.035
MIN_DETECT_SCORE = 0.40
REQUIRED_LANDMARKS = 5

LANDMARK_COLOR = (200, 212, 0)
CONTOUR_COLOR = (0, 212, 200)
KEY_COLOR = (62, 224, 176)

# Canonical 68-point face in a 0-1 box (iBUG-style), plus 5 YuNet anchors.
# Order: right eye, left eye, nose, right mouth, left mouth (YuNet).
_TEMPLATE_68 = np.array([
    [0.16, 0.38], [0.17, 0.48], [0.19, 0.58], [0.21, 0.67], [0.25, 0.75],
    [0.31, 0.82], [0.38, 0.87], [0.45, 0.91], [0.50, 0.92], [0.55, 0.91],
    [0.62, 0.87], [0.69, 0.82], [0.75, 0.75], [0.79, 0.67], [0.81, 0.58],
    [0.83, 0.48], [0.84, 0.38],
    [0.24, 0.30], [0.29, 0.26], [0.36, 0.25], [0.42, 0.27], [0.46, 0.30],
    [0.54, 0.30], [0.58, 0.27], [0.64, 0.25], [0.71, 0.26], [0.76, 0.30],
    [0.50, 0.36], [0.50, 0.42], [0.50, 0.48], [0.50, 0.54],
    [0.43, 0.58], [0.47, 0.60], [0.50, 0.61], [0.53, 0.60], [0.57, 0.58],
    [0.30, 0.37], [0.34, 0.35], [0.38, 0.35], [0.42, 0.37], [0.38, 0.38], [0.34, 0.38],
    [0.58, 0.37], [0.62, 0.35], [0.66, 0.35], [0.70, 0.37], [0.66, 0.38], [0.62, 0.38],
    [0.36, 0.70], [0.41, 0.68], [0.46, 0.67], [0.50, 0.68], [0.54, 0.67], [0.59, 0.68],
    [0.64, 0.70], [0.59, 0.75], [0.54, 0.78], [0.50, 0.79], [0.46, 0.78], [0.41, 0.75],
    [0.39, 0.70], [0.46, 0.71], [0.50, 0.72], [0.54, 0.71], [0.61, 0.70],
    [0.54, 0.73], [0.50, 0.74], [0.46, 0.73],
], dtype=np.float32)

_TEMPLATE_5 = np.array([
    _TEMPLATE_68[36:42].mean(axis=0),  # right eye
    _TEMPLATE_68[42:48].mean(axis=0),  # left eye
    _TEMPLATE_68[30],                  # nose
    _TEMPLATE_68[48],                  # right mouth
    _TEMPLATE_68[54],                  # left mouth
], dtype=np.float32)

_JAW = list(range(0, 17))
_RBROW = list(range(17, 22))
_LBROW = list(range(22, 27))
_NOSE = list(range(27, 36))
_REYE = list(range(36, 42))
_LEYE = list(range(42, 48))
_MOUTH = list(range(48, 60))
_CONTOURS = (_JAW, _RBROW, _LBROW, _NOSE, _REYE, _LEYE, _MOUTH)
_OVAL = _JAW + _LBROW[::-1] + _RBROW[::-1]


def ensure_face_model():
    os.makedirs(os.path.dirname(YUNET_PATH), exist_ok=True)
    if os.path.isfile(YUNET_PATH) and os.path.getsize(YUNET_PATH) > 50_000:
        return YUNET_PATH
    last_error = None
    for url in YUNET_URLS:
        try:
            print("[FACE] Downloading YuNet face model...")
            urllib.request.urlretrieve(url, YUNET_PATH)
            if os.path.isfile(YUNET_PATH) and os.path.getsize(YUNET_PATH) > 50_000:
                print("[FACE] Saved", YUNET_PATH)
                return YUNET_PATH
        except Exception as exc:
            last_error = exc
    raise FileNotFoundError(f"Could not download YuNet model: {last_error}")


def _inside_gate(x, y):
    return ((x - OVAL_CX) / OVAL_RX) ** 2 + ((y - OVAL_CY) / OVAL_RY) ** 2 <= 1.0


def _near_gate_center(x, y, frac=CENTER_FRAC):
    """True when (x, y) is in the middle zone of the face-gate oval."""
    rx = max(1e-6, OVAL_RX * frac)
    ry = max(1e-6, OVAL_RY * frac)
    return ((x - OVAL_CX) / rx) ** 2 + ((y - OVAL_CY) / ry) ** 2 <= 1.0


def _in_frame(x, y, margin=0.02):
    return -margin <= x <= 1.0 + margin and -margin <= y <= 1.0 + margin


def _five_from_yunet(face, width, height):
    pts = []
    for index in range(5):
        x = float(face[4 + index * 2]) / float(width)
        y = float(face[5 + index * 2]) / float(height)
        pts.append((x, y))
    return pts


def landmarks_complete(points5, box=None):
    if not points5 or len(points5) < REQUIRED_LANDMARKS:
        return False
    if any(not _in_frame(x, y) for x, y in points5):
        return False
    right_eye, left_eye, nose, right_mouth, left_mouth = points5
    xs = [p[0] for p in points5]
    ys = [p[1] for p in points5]
    if max(xs) - min(xs) < MIN_FACE_WIDTH:
        return False
    if max(ys) - min(ys) < MIN_FACE_HEIGHT * 0.45:
        return False
    eye_dist = ((left_eye[0] - right_eye[0]) ** 2 + (left_eye[1] - right_eye[1]) ** 2) ** 0.5
    if eye_dist < MIN_EYE_DIST:
        return False
    if nose[1] <= min(left_eye[1], right_eye[1]):
        return False
    if min(left_mouth[1], right_mouth[1]) <= nose[1]:
        return False
    if box is not None:
        _, _, bw, bh = box
        if bw < MIN_FACE_WIDTH or bh < MIN_FACE_HEIGHT:
            return False
    return True


def face_in_region(points5, box=None):
    """True only when the face is centered in the middle of the gate oval."""
    if box is not None:
        x, y, bw, bh = box
        if bw < MIN_FACE_WIDTH or bh < MIN_FACE_HEIGHT:
            return False
        cx, cy = x + bw / 2.0, y + bh / 2.0
        if not _near_gate_center(cx, cy):
            return False
    if points5:
        xs = [float(p[0]) for p in points5]
        ys = [float(p[1]) for p in points5]
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        if not _near_gate_center(cx, cy):
            return False
        inside = sum(1 for px, py in points5 if _inside_gate(px, py))
        return inside / len(points5) >= IN_REGION_RATIO
    return box is not None


def choose_staff_match(
    best,
    score,
    current_id,
    threshold=0.90,
    hold=0.75,
    margin=None,
    min_margin=0.025,
):
    """One face at a time, matched against every enrolled staff.

    Full-threshold hits need a margin over the runner-up before switching
    (or locking on cold start). Soft hold keeps the person already on screen.
    """
    if not best or score is None or score < 0:
        return None
    best_id = str(best.get("staff_id"))
    same = current_id is not None and best_id == str(current_id)
    if score >= threshold:
        if same:
            return best
        if margin is not None and margin < min_margin:
            return None
        return best
    if same and score >= hold:
        return best
    return None


def _align_template(points5):
    detected = np.array(points5, dtype=np.float32)
    matrix, _ = cv2.estimateAffinePartial2D(_TEMPLATE_5, detected, method=cv2.LMEDS)
    if matrix is None:
        return None
    ones = np.ones((len(_TEMPLATE_68), 1), dtype=np.float32)
    hom = np.hstack([_TEMPLATE_68, ones])
    aligned = hom @ matrix.T
    return [(float(x), float(y)) for x, y in aligned]


def mask_face_region(frame, mesh):
    """Keep only the facial oval. Everything else becomes black."""
    if frame is None or not mesh or len(mesh) < 17:
        return None
    height, width = frame.shape[:2]
    contour = np.array(
        [[int(mesh[idx][0] * width), int(mesh[idx][1] * height)] for idx in _OVAL if idx < len(mesh)],
        dtype=np.int32,
    )
    if contour.shape[0] < 8:
        return None
    mask = np.zeros((height, width), dtype=np.uint8)
    cv2.fillPoly(mask, [contour], 255)
    x, y, box_w, box_h = cv2.boundingRect(contour)
    pad = 6
    x1 = max(0, x - pad)
    y1 = max(0, y - pad)
    x2 = min(width, x + box_w + pad)
    y2 = min(height, y + box_h + pad)
    if x2 - x1 < 24 or y2 - y1 < 24:
        return None
    crop = frame[y1:y2, x1:x2].copy()
    crop_mask = mask[y1:y2, x1:x2]
    isolated = np.zeros_like(crop)
    isolated[crop_mask > 0] = crop[crop_mask > 0]
    return isolated


def crop_from_box(frame, face, pad=8):
    if frame is None or face is None:
        return None
    height, width = frame.shape[:2]
    x, y, box_w, box_h = [int(float(value)) for value in face[:4]]
    x1 = max(0, x - pad)
    y1 = max(0, y - pad)
    x2 = min(width, x + box_w + pad)
    y2 = min(height, y + box_h + pad)
    if x2 - x1 < 24 or y2 - y1 < 24:
        return None
    return frame[y1:y2, x1:x2].copy()


def encode_crop(crop):
    if crop is None:
        return None
    ok, encoded = cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 92])
    return encoded.tobytes() if ok else None


def draw_landmarks(frame, mesh, points5):
    vis = frame.copy()
    height, width = vis.shape[:2]
    if mesh:
        pts = [(int(x * width), int(y * height)) for x, y in mesh]
        for loop in _CONTOURS:
            for start, end in zip(loop, loop[1:]):
                if start < len(pts) and end < len(pts):
                    cv2.line(vis, pts[start], pts[end], CONTOUR_COLOR, 1, cv2.LINE_AA)
            if loop in (_REYE, _LEYE, _MOUTH) and loop[0] < len(pts) and loop[-1] < len(pts):
                cv2.line(vis, pts[loop[-1]], pts[loop[0]], CONTOUR_COLOR, 1, cv2.LINE_AA)
        for point in pts:
            cv2.circle(vis, point, 1, LANDMARK_COLOR, -1, cv2.LINE_AA)
    for x, y in points5 or []:
        cv2.circle(vis, (int(x * width), int(y * height)), 3, KEY_COLOR, -1, cv2.LINE_AA)
    return vis


class FaceGate:
    def __init__(self):
        self.detector = None
        self.cascade = None
        self.backend = None
        self._input_size = None

    def load(self):
        if self.detector is not None or self.cascade is not None:
            return self.backend
        try:
            model_path = ensure_face_model()
            self.detector = cv2.FaceDetectorYN.create(
                model_path,
                "",
                (320, 320),
                score_threshold=0.35,
                nms_threshold=0.3,
                top_k=10,
            )
            self.backend = "yunet"
            print("[FACE] Loaded OpenCV YuNet face detector")
            return self.backend
        except Exception as exc:
            print("[FACE] YuNet unavailable, using Haar cascade:", exc)

        cascade_path = os.path.join(cv2.data.haarcascades, "haarcascade_frontalface_default.xml")
        self.cascade = cv2.CascadeClassifier(cascade_path)
        if self.cascade.empty():
            raise RuntimeError("Could not load a face detector")
        self.backend = "haar"
        print("[FACE] Loaded Haar face cascade")
        return self.backend

    def _detect_yunet(self, frame):
        height, width = frame.shape[:2]
        size = (width, height)
        if self._input_size != size:
            self.detector.setInputSize(size)
            self._input_size = size
        _, faces = self.detector.detect(frame)
        if faces is None or len(faces) == 0:
            return None
        best = None
        best_rank = -1e9
        for face in faces:
            score = float(face[-1])
            if score < MIN_DETECT_SCORE:
                continue
            area = float(face[2]) * float(face[3])
            rank = area * (0.5 + score)
            if rank > best_rank:
                best_rank = rank
                best = face
        return best

    def _detect_haar(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(gray, 1.15, 5, minSize=(80, 80))
        if len(faces) == 0:
            return None
        height, width = frame.shape[:2]
        cx, cy = OVAL_CX * width, OVAL_CY * height
        x, y, bw, bh = min(
            faces,
            key=lambda box: (box[0] + box[2] / 2 - cx) ** 2 + (box[1] + box[3] / 2 - cy) ** 2,
        )
        # Approximate the same 5 landmarks from a frontal face box.
        return np.array([
            x, y, bw, bh,
            x + bw * 0.30, y + bh * 0.38,
            x + bw * 0.70, y + bh * 0.38,
            x + bw * 0.50, y + bh * 0.55,
            x + bw * 0.35, y + bh * 0.75,
            x + bw * 0.65, y + bh * 0.75,
            0.66,
        ], dtype=np.float32)

    def process(self, frame, draw=True):
        info = {
            "detected": False,
            "complete": False,
            "in_region": False,
            "landmark_count": 0,
            "crop": None,
            "crop_bytes": None,
            "mesh": None,
            "points5": None,
        }
        if frame is None:
            return frame, info
        if self.detector is None and self.cascade is None:
            self.load()

        height, width = frame.shape[:2]
        face = self._detect_yunet(frame) if self.detector is not None else self._detect_haar(frame)
        vis = frame
        if face is None:
            return vis, info

        points5 = _five_from_yunet(face, width, height)
        box = (
            float(face[0]) / width,
            float(face[1]) / height,
            float(face[2]) / width,
            float(face[3]) / height,
        )
        mesh = _align_template(points5) or []
        info["detected"] = True
        info["mesh"] = mesh
        info["points5"] = points5
        info["landmark_count"] = len(mesh) if mesh else len(points5)
        info["complete"] = landmarks_complete(points5, box)
        info["in_region"] = face_in_region(points5, box)
        crop = mask_face_region(frame, mesh) if mesh else None
        if crop is None:
            crop = crop_from_box(frame, face)
        info["crop"] = crop
        info["crop_bytes"] = encode_crop(crop)
        if draw:
            vis = draw_landmarks(frame, mesh, points5)
        return vis, info

    def close(self):
        self.detector = None
        self.cascade = None
        self._input_size = None


def _self_check():
    # Centered face in gate middle → accept
    assert face_in_region(
        [(0.48, 0.48), (0.52, 0.48), (0.50, 0.52), (0.47, 0.55), (0.53, 0.55)],
        (0.42, 0.38, 0.16, 0.24),
    )
    # Too small / off-center → reject
    assert not face_in_region([(0.5, 0.5)], (0.0, 0.0, 0.02, 0.02))
    assert not face_in_region(
        [(0.12, 0.20), (0.18, 0.20), (0.15, 0.28), (0.12, 0.32), (0.18, 0.32)],
        (0.08, 0.12, 0.16, 0.24),
    )
    ali = {"staff_id": "1", "staff_name": "Ali"}
    sara = {"staff_id": "2", "staff_name": "Sara"}
    # Cold start: needs margin over runner-up
    assert choose_staff_match(sara, 0.93, None, margin=0.08)["staff_name"] == "Sara"
    assert choose_staff_match(sara, 0.93, None, margin=0.01) is None
    # Same person: no margin required
    assert choose_staff_match(ali, 0.93, "1", margin=0.0)["staff_id"] == "1"
    # Soft hold keeps current person
    assert choose_staff_match(ali, 0.76, "1")["staff_id"] == "1"
    assert choose_staff_match(sara, 0.76, "1") is None
    # Switch needs margin
    assert choose_staff_match(sara, 0.93, "1", margin=0.01) is None
    assert choose_staff_match(sara, 0.93, "1", margin=0.08)["staff_name"] == "Sara"
    assert choose_staff_match(None, -1, None) is None


if __name__ == "__main__":
    _self_check()
    print("face checks ok")
