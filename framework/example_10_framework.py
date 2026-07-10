from behavior_engine import BehaviorEngine

robot = BehaviorEngine("eth0", loop_interval=1.0, cooldown=3.0)

# ──────────────────────────────────────────────
# 10. Avançado — interação social completa
# ──────────────────────────────────────────────
robot.load_many([
   "reject if person is within 0.4 meters",
   "hug if person is within 0.8 meters",
   "shake hand if person is within 1.2 meters",
   "high five if person is within 1.8 meters",
   "clap if chair is farther than 1.0 meters",
])
robot.run()
