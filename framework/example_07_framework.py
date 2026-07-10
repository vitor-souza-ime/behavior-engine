from behavior_engine import BehaviorEngine

robot = BehaviorEngine("eth0", loop_interval=1.0, cooldown=3.0)

# ──────────────────────────────────────────────
# 7. Intermediário — duas zonas de distância
# ──────────────────────────────────────────────
robot.load_many([
   "reject if person is within 0.5 meters",
   "shake hand if person is within 1.5 meters",
])
robot.run()
