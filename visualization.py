import matplotlib.pyplot as plt


def draw_finger(points):

    # Separate x and y coordinates
    x = [point[0] for point in points]
    y = [point[1] for point in points]

    plt.figure(figsize=(6,6))

    # Draw finger
    plt.plot(
        x,
        y,
        '-o',
        linewidth=4,
        markersize=8
    )

    # Draw joints
    for i, point in enumerate(points):
        plt.text(point[0], point[1]+2, f"J{i}")

    plt.title("Virtual Prosthetic Finger")

    plt.xlabel("X Position (mm)")
    plt.ylabel("Y Position (mm)")

    plt.grid(True)

    plt.axis("equal")

    plt.xlim(-20,120)
    plt.ylim(-20,120)

    plt.show()

