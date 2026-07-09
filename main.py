import matplotlib.pyplot as plt
from finger import Finger
from kinematics import forward_kinematics

# Create finger
index_finger = Finger(
    "Index Finger",
    50,
    30,
    20
)

# Turn interactive mode on
plt.ion()

figure, ax = plt.subplots(figsize=(6,6))

for angle in range(0, 81, 2):

    # Change finger angles
    index_finger.set_angles(
        mcp=angle,
        pip=angle * 0.75,
        dip=angle * 0.5
    )

    # Calculate joint positions
    points = forward_kinematics(index_finger)

    # Separate x and y coordinates
    x = [point[0] for point in points]
    y = [point[1] for point in points]

    # Clear previous frame
    ax.clear()

    # Draw finger
    ax.plot(
        x,
        y,
        '-o',
        linewidth=4,
        markersize=10
    )

    # Label joints
    for i, point in enumerate(points):
        ax.text(point[0], point[1] + 2, f"J{i}")

    ax.set_title("Virtual Prosthetic Finger")

    ax.set_xlabel("X Position (mm)")
    ax.set_ylabel("Y Position (mm)")

    ax.grid(True)

    ax.axis("equal")

    ax.set_xlim(-20,120)
    ax.set_ylim(-20,120)

    plt.pause(0.05)

plt.ioff()
plt.show()


