from finger import Finger
from kinematics import forward_kinematics

index_finger = Finger(
    "Index Finger",
    50,
    30,
    20
)

index_finger.set_angles(
    20,
    45,
    15
)

index_finger.print_info()

points = forward_kinematics(index_finger)

print("\nJoint Positions")

for i, point in enumerate(points):
    print(f"Point {i}: {point}")


