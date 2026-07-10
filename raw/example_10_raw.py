import time
from ultralytics import YOLO
import pyrealsense2 as rs
import numpy as np
from depth_utils import get_object_distance

# ──────────────────────────────────────────────
# 10. Avançado — interação social completa (SEM FRAMEWORK)
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

last_action_time = {
    "reject": 0.0,
    "hug": 0.0,
    "shake_hand": 0.0,
    "high_five": 0.0,
    "clap": 0.0,
}

REJECT_THRESHOLD_METERS = 0.4
HUG_THRESHOLD_METERS = 0.8
SHAKE_HAND_THRESHOLD_METERS = 1.2
HIGH_FIVE_THRESHOLD_METERS = 1.8
CHAIR_FAR_THRESHOLD_METERS = 1.0

def send_action(name):
    print(f"[ACTION] Executando: {name}")

def get_frames():
    frames = pipeline.wait_for_frames()
    aligned = align.process(frames)
    color_frame = aligned.get_color_frame()
    depth_frame = aligned.get_depth_frame()
    if not color_frame or not depth_frame:
        return None, None
    return np.asanyarray(color_frame.get_data()), depth_frame

def maybe_trigger(action_name, condition, current_time):
    if condition and (current_time - last_action_time[action_name]) > COOLDOWN:
        send_action(action_name)
        last_action_time[action_name] = current_time

try:
    while True:
        color_image, depth_frame = get_frames()
        if color_image is None:
            time.sleep(LOOP_INTERVAL)
            continue

        results = model(color_image, verbose=False)[0]

        min_person_distance = None
        min_chair_distance = None

        for box in results.boxes:
            cls_name = model.names[int(box.cls)]
            distance = get_object_distance(depth_frame, box, depth_scale)
            if distance is None:
                continue

            if cls_name == "person":
                if min_person_distance is None or distance < min_person_distance:
                    min_person_distance = distance
            elif cls_name == "chair":
                if min_chair_distance is None or distance < min_chair_distance:
                    min_chair_distance = distance

        current_time = time.time()

        if min_person_distance is not None:
            # Regras de pessoa, em ordem de prioridade por proximidade
            if min_person_distance <= REJECT_THRESHOLD_METERS:
                maybe_trigger("reject", True, current_time)
            elif min_person_distance <= HUG_THRESHOLD_METERS:
                maybe_trigger("hug", True, current_time)
            elif min_person_distance <= SHAKE_HAND_THRESHOLD_METERS:
                maybe_trigger("shake_hand", True, current_time)
            elif min_person_distance <= HIGH_FIVE_THRESHOLD_METERS:
                maybe_trigger("high_five", True, current_time)

        # Regra independente: clap se cadeira detectada e distante
        if min_chair_distance is not None and min_chair_distance > CHAIR_FAR_THRESHOLD_METERS:
            maybe_trigger("clap", True, current_time)

        time.sleep(LOOP_INTERVAL)

except KeyboardInterrupt:
    pipeline.stop()
    print("Encerrado pelo usuário.")
