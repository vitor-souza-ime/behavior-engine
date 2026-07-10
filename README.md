# 🤖 BehaviorEngine

**A lightweight, natural-language, rule-based framework for reactive humanoid robot behavior.**

BehaviorEngine lets you program social and reactive behaviors for the **Unitree G1 EDU** humanoid robot using plain English sentences instead of imperative code. It sits on top of `EmbodiedAI`, a unified abstraction layer over the Unitree SDK2, an Intel RealSense depth camera, and a YOLO object detector.

```python
from behavior_engine import BehaviorEngine

robot = BehaviorEngine("eth0", loop_interval=1.0, cooldown=3.0)

robot.load_many([
    "reject if person is within 0.4 meters",
    "hug if person is within 0.8 meters",
    "shake hand if person is within 1.2 meters",
    "high five if person is within 1.8 meters",
    "clap if chair is farther than 1.0 meters",
])

robot.run()
```

That's it. No manual camera setup, no distance math, no cooldown timers, no `if/elif` chains.

---

## ✨ Why BehaviorEngine?

| 🚫 Without the framework | ✅ With BehaviorEngine |
|---|---|
| ~76 lines of code per behavior | ~12 lines of code per behavior |
| Manual YOLO + RealSense pipeline setup | Handled internally |
| Manual distance thresholds & `if` chains | One natural-language sentence per rule |
| Manual cooldown/debounce logic per action | Built-in, automatic |
| Cyclomatic complexity up to 16+ | Cyclomatic complexity of 1 |

These numbers come from a controlled experiment comparing direct implementations against BehaviorEngine across ten social-interaction scenarios. See the [`raw/`](./raw) folder for the paired code samples used in the comparison.

---

## 🧠 How it works

```
┌─────────────────────────────┐
│   "shake hand if person     │
│    is within 1.0 meters"    │
└──────────────┬───────────────┘
               │  parsed by Rule
               ▼
┌─────────────────────────────┐
│ action = shake_hand         │
│ class  = person             │
│ operator = "<"              │
│ threshold = 1.0 m           │
└──────────────┬───────────────┘
               │  evaluated every cycle
               ▼
┌─────────────────────────────┐
│   YOLO detection + RealSense │
│      depth (EmbodiedAI)      │
└──────────────┬───────────────┘
               │  match found + cooldown OK
               ▼
┌─────────────────────────────┐
│   robot.shake_hand()          │
└─────────────────────────────┘
```

1. 📝 **Parse** — a lightweight regex-based interpreter (`Rule`) maps a sentence like `"clap if chair"` or `"hands up if person is farther than 2.0 meters"` into an action, a target object class, a relational operator, and a distance threshold.
2. 👁️ **Perceive** — each cycle, `EmbodiedAI` captures an RGB-D frame, runs YOLO detection, and estimates the median depth (in meters) to every detected object.
3. ⚖️ **Evaluate** — every loaded rule is checked against the current detections.
4. ⏱️ **Cooldown** — a rule only fires again after a configurable cooldown period has elapsed, preventing action spam.
5. 🦾 **Act** — the matched rule triggers the corresponding robot method (arm gesture, locomotion, posture, etc.) through the Unitree SDK2.

---

## 📦 Repository structure

```
behavior-engine/
├── framework/     🧩 Core library: BehaviorEngine, Rule, EmbodiedAI
└── raw/           📊 Paired code samples (with vs. without the framework)
                     used for the complexity/LOC comparison experiment
```

---

## 🚀 Getting started

### Requirements

- 🐍 Python 3.9+
- 🦿 [Unitree SDK2](https://github.com/unitreerobotics/unitree_sdk2) (`unitree_sdk2py`)
- 📷 Intel RealSense camera + `pyrealsense2`
- 🎯 [Ultralytics YOLO](https://github.com/ultralytics/ultralytics) (`ultralytics`)
- 🔥 PyTorch (GPU optional, falls back to CPU automatically)

### Installation

```bash
git clone https://github.com/vitor-souza-ime/behavior-engine.git
cd behavior-engine/framework
pip install ultralytics pyrealsense2 torch numpy
# plus unitree_sdk2py, following Unitree's official installation instructions
```

### Basic usage

```python
from behavior_engine import BehaviorEngine

robot = BehaviorEngine("eth0")          # network interface for the DDS channel
robot.load("shake hand if person")      # a single rule, no distance threshold
robot.run()                             # Ctrl+C to stop
```

### Multiple concurrent rules

```python
robot.load_many([
    "reject if person is within 0.5 meters",
    "shake hand if person is within 1.5 meters",
    "hands up if person is farther than 1.5 meters",
])
robot.run()
```

---

## 📖 Rule syntax

Rules follow a simple pattern:

```
<action> if [you detect/see] <class> [operator] <distance> meter(s)
```

**Examples:**

| Sentence | Meaning |
|---|---|
| `shake hand if person` | Shake hands whenever a person is detected, any distance |
| `clap if chair` | Clap whenever a chair is detected |
| `reject if person is within 0.5 meters` | Reject gesture when a person is closer than 0.5 m |
| `hands up if person is farther than 2.0 meters` | Raise hands when a person is farther than 2 m |
| `clap if chair is farther than 1.0 meters` | Clap when a chair is farther than 1 m |

### 🔤 Supported comparison expressions

| Expression | Operator |
|---|---|
| `closer than`, `less than`, `within`, `nearer than` | `<` |
| `farther than`, `further than`, `more than`, `beyond` | `>` |
| `at least`, `no closer than` | `>=` |
| `at most`, `no farther than` | `<=` |

### 🎯 Recognized object classes (aliases)

`person`, `people`, `human` → `person` · `chair` · `table` · `bottle` · `dog` · `cat` · `laptop` · `phone`, `cell phone` → `cell phone`

### 🙌 Available actions

Any public method of `EmbodiedAI` is automatically exposed as an action, including:

- 🤝 `shake_hand`, `high_five`, `hug`, `heart`, `right_heart`
- ✋ `hands_up`, `right_hand_up`, `reject`, `x_ray`
- 👋 `high_wave`, `face_wave`, `wave_hand`
- 😘 `left_kiss`, `right_kiss`, `two_hand_kiss`
- 👏 `clap`
- 🚶 `move_forward`, `move_lateral`, `move_rotate`, `stop`
- 🧍 `low_stand`, `high_stand`, `damp`, `zero_torque`

Call `robot.available_actions()` and `robot.available_classes()` to list them programmatically.

---

## 🛠️ Core API

| Method | Description |
|---|---|
| `load(rule_string)` | Parse and register a single natural-language rule |
| `load_many(rules)` | Load a list of rules at once |
| `clear_rules()` | Remove all loaded rules |
| `step()` | Run a single perception + evaluation cycle |
| `run()` | Run the main loop continuously until `Ctrl+C` |
| `available_actions()` | List all recognized action names |
| `available_classes()` | List all recognized object classes |

---

## 🦾 Under the hood: `EmbodiedAI`

`EmbodiedAI` is the abstraction layer that `BehaviorEngine` builds upon. It unifies:

- 🎯 **Perception** — YOLO-based object detection (`detect()`, `detect_with_distance()`) with automatic GPU/CPU fallback
- 📏 **Depth estimation** — median-filtered RealSense depth lookup per bounding box (`object_distance()`)
- 💪 **Arm gestures** — via `G1ArmActionClient`
- 🚶 **Locomotion & posture** — via `LocoClient`

It can also be used standalone, without the rule engine:

```python
from embodied_ai import EmbodiedAI

robot = EmbodiedAI("eth0")
robot.clap()
robot.move_forward(0.3)

detections = robot.detect_with_distance()
# [{"class": "person", "confidence": 0.91, "bbox": (x1, y1, x2, y2),
#   "center": (cx, cy), "distance_m": 1.42}, ...]
```

---

## 📊 Measured impact

Across ten paired social-interaction scenarios (see [`raw/`](./raw)):

- 📉 **~84%** average reduction in total lines of code
- 📉 **~88%** average reduction in logical lines of code
- 🧹 **100%** elimination of conditional branches and function-level cyclomatic complexity in user-facing scripts
- ⚙️ **~41%** reduction in manually declared configuration units (thresholds, timers, callbacks)

---

## 📄 Citation

If you use BehaviorEngine in academic work, please cite the associated paper (in preparation, Instituto Militar de Engenharia — IME).

---

## 📝 License

See the repository for license details.

---

## 🙋 Contributing

Issues and pull requests are welcome.
