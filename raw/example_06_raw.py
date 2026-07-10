import time
from ultralytics import YOLO
import pyrealsense2 as rs
import numpy as np

# ──────────────────────────────────────────────
# 6. Intermediário — duas regras, pessoa e cadeira (SEM FRAMEWORK)
# ──────────────────────────────────────────────

model = YOLO("yolov8n.pt")

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

LOOP_INTERVAL = 1.0
COOLDOWN = 3.0
last_action_time_clap = 0.0
last_action_time_shake = 0.0

def send_action_clap():
    print("[ACTION] Executando: clap")
    # g1_sdk.execute_motion("clap")

def send_action_shake_hand():
    print("[ACTION] Executando: shake_hand")
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

        chair_detected = "chair" in detected_classes
        person_detected = "person" in detected_classes

        current_time = time.time()

        # Regra 1: clap se cadeira detectada
        if chair_detected and (current_time - last_action_time_clap) > COOLDOWN:
            send_action_clap()
            last_action_time_clap = current_time

        # Regra 2: shake hand se pessoa detectada
        if person_detected and (current_time - last_action_time_shake) > COOLDOWN:
            send_action_shake_hand()
            last_action_time_shake = current_time

        time.sleep(LOOP_INTERVAL)

except KeyboardInterrupt:
    pipeline.stop()
    print("Encerrado pelo usuário.")
