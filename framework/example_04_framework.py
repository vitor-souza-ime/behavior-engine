from behavior_engine import BehaviorEngine

robot = BehaviorEngine("eth0", loop_interval=1.0, cooldown=3.0)

# ──────────────────────────────────────────────
# 4. Intermediário — pessoa longe, levanta as mãos
# ──────────────────────────────────────────────
robot.load_many([
   "hands up if person is farther than 2.0 meters",
])
robot.run()
