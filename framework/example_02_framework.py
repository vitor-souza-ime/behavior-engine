from behavior_engine import BehaviorEngine

robot = BehaviorEngine("eth0", loop_interval=1.0, cooldown=3.0)

# ──────────────────────────────────────────────
# 2. Básico — detecta uma cadeira pessoa e aplaude
# ──────────────────────────────────────────────

robot.load_many([
   "clap if chair",
])
robot.run()
