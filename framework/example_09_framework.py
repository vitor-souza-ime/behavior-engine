from behavior_engine import BehaviorEngine

robot = BehaviorEngine("eth0", loop_interval=1.0, cooldown=3.0)

# ──────────────────────────────────────────────
# 9. Avançado — gesto social por proximidade
# ──────────────────────────────────────────────
robot.load_many([
   "hug if person is within 0.6 meters",
   "high five if person is within 1.2 meters",
   "clap if person is farther than 1.2 meters",
])
robot.run()
