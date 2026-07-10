from behavior_engine import BehaviorEngine

robot = BehaviorEngine("eth0", loop_interval=1.0, cooldown=3.0)

# ──────────────────────────────────────────────
# 5. Intermediário — aperto de mão em distância média
# ──────────────────────────────────────────────
robot.load_many([
   "shake hand if person is within 1.0 meters",
])
robot.run()
