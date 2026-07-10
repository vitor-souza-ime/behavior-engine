import time
import cv2
from ultralytics import YOLO
import pyrealsense2 as rs
import numpy as np

# ──────────────────────────────────────────────
# 1. Básico — detecta qualquer pessoa e acena (SEM FRAMEWORK)
# ──────────────────────────────────────────────

model = YOLO("yolov8n.pt")

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

LOOP_INTERVAL = 1.0
COOLDOWN = 3.0
last_action_time = 0.0

def send_action_shake_hand():
    print("[ACTION] Executando: shake_hand")
    # Aqui entraria a chamada real ao SDK do G1 EDU
    # g1_sdk.execute_motion("shake_hand")

def get_frame():
    frames = pipeline.wait_for_frames()
    color_frame = frames.get_color_frame()
    if not color_frame:
        return None
    return np.asanyarray(color_frame.get_data())

try:
    while True:
        frame = get_frame()
        if frame is None:
            time.sleep(LOOP_INTERVAL)
            continue

        results = model(frame, verbose=False)[0]
        detected_classes = [model.names[int(box.cls)] for box in results.boxes]

        person_detected = "person" in detected_classes

        current_time = time.time()
        if person_detected and (current_time - last_action_time) > COOLDOWN:
            send_action_shake_hand()
            last_action_time = current_time

        time.sleep(LOOP_INTERVAL)

except KeyboardInterrupt:
    pipeline.stop()
    print("Encerrado pelo usuário.")
