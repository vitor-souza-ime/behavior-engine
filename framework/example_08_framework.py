from behavior_engine import BehaviorEngine

robot = BehaviorEngine("eth0", loop_interval=1.0, cooldown=3.0)

# ──────────────────────────────────────────────
# 8. Avançado — três zonas de distância
# ──────────────────────────────────────────────
robot.load_many([
   "reject if person is within 0.5 meters",
   "shake hand if person is within 1.5 meters",
   "hands up if person is farther than 1.5 meters",
])
robot.run()
