import time
from ultralytics import YOLO
import pyrealsense2 as rs
import numpy as np
from depth_utils import get_object_distance

# ──────────────────────────────────────────────
# 9. Avançado — gesto social por proximidade (SEM FRAMEWORK)
# ──────────────────────────────────────────────

model = YOLO("yolov8n.pt")

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
profile = pipeline.start(config)

depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()

align = rs.align(rs.stream.color)

LOOP_INTERVAL = 1.0
COOLDOWN = 3.0
last_action_time_hug = 0.0
last_action_time_high_five = 0.0
last_action_time_clap = 0.0

HUG_THRESHOLD_METERS = 0.6
HIGH_FIVE_THRESHOLD_METERS = 1.2

def send_action_hug():
    print("[ACTION] Executando: hug")

def send_action_high_five():
    print("[ACTION] Executando: high_five")

def send_action_clap():
    print("[ACTION] Executando: clap")

def get_frames():
    frames = pipeline.wait_for_frames()
    aligned = align.process(frames)
    color_frame = aligned.get_color_frame()
    depth_frame = aligned.get_depth_frame()
    if not color_frame or not depth_frame:
        return None, None
    return np.asanyarray(color_frame.get_data()), depth_frame

try:
    while True:
        color_image, depth_frame = get_frames()
        if color_image is None:
            time.sleep(LOOP_INTERVAL)
            continue

        results = model(color_image, verbose=False)[0]

        min_person_distance = None
        for box in results.boxes:
            cls_name = model.names[int(box.cls)]
            if cls_name != "person":
                continue
            distance = get_object_distance(depth_frame, box, depth_scale)
            if distance is not None:
                if min_person_distance is None or distance < min_person_distance:
                    min_person_distance = distance

        current_time = time.time()

        if min_person_distance is not None:
            # Regra 1: hug se muito perto
            if min_person_distance <= HUG_THRESHOLD_METERS:
                if (current_time - last_action_time_hug) > COOLDOWN:
                    send_action_hug()
                    last_action_time_hug = current_time

            # Regra 2: high five se distância média
            elif min_person_distance <= HIGH_FIVE_THRESHOLD_METERS:
                if (current_time - last_action_time_high_five) > COOLDOWN:
                    send_action_high_five()
                    last_action_time_high_five = current_time

            # Regra 3: clap se longe
            else:
                if (current_time - last_action_time_clap) > COOLDOWN:
                    send_action_clap()
                    last_action_time_clap = current_time

        time.sleep(LOOP_INTERVAL)

except KeyboardInterrupt:
    pipeline.stop()
    print("Encerrado pelo usuário.")
