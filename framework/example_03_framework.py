from behavior_engine import BehaviorEngine

robot = BehaviorEngine("eth0", loop_interval=1.0, cooldown=3.0)

# ──────────────────────────────────────────────
# 3. Básico — pessoa muito perto, rejeita
# ──────────────────────────────────────────────
robot.load_many([
   "reject if person is within 0.5 meters",
])
robot.run()
