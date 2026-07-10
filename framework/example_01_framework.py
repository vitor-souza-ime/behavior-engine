from behavior_engine import BehaviorEngine

robot = BehaviorEngine("eth0", loop_interval=1.0, cooldown=3.0)

# ──────────────────────────────────────────────
# 1. Básico — detecta qualquer pessoa e acena
# ──────────────────────────────────────────────

robot.load_many([
   "shake hand if person",
])
robot.run()
