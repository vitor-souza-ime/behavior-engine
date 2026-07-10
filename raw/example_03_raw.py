import time
from ultralytics import YOLO
import pyrealsense2 as rs
import numpy as np
from depth_utils import get_object_distance

# ──────────────────────────────────────────────
# 3. Básico — pessoa muito perto, rejeita (SEM FRAMEWORK)
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
last_action_time = 0.0

REJECT_THRESHOLD_METERS = 0.5

def send_action_reject():
    print("[ACTION] Executando: reject")
    # g1_sdk.execute_motion("reject")

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

        person_too_close = False
        for box in results.boxes:
            cls_name = model.names[int(box.cls)]
            if cls_name != "person":
                continue
            distance = get_object_distance(depth_frame, box, depth_scale)
            if distance is not None and distance <= REJECT_THRESHOLD_METERS:
                person_too_close = True
                break

        current_time = time.time()
        if person_too_close and (current_time - last_action_time) > COOLDOWN:
            send_action_reject()
            last_action_time = current_time

        time.sleep(LOOP_INTERVAL)

except KeyboardInterrupt:
    pipeline.stop()
    print("Encerrado pelo usuário.")
