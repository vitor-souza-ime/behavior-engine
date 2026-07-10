from behavior_engine import BehaviorEngine

robot = BehaviorEngine("eth0", loop_interval=1.0, cooldown=3.0)

# ──────────────────────────────────────────────
# 6. Intermediário — duas regras, pessoa e cadeira
# ──────────────────────────────────────────────
robot.load_many([
   "clap if chair",
   "shake hand if person",
])
robot.run()
