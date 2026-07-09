import matplotlib.pyplot as plt


class FingerVisualizer:

    def __init__(self):

        self.fig, self.ax = plt.subplots(figsize=(7,7))

        plt.subplots_adjust(bottom=0.30)

    def draw(self, points):

        self.ax.clear()

        x = [p[0] for p in points]
        y = [p[1] for p in points]

        self.ax.plot(
            x,
            y,
            "-o",
            linewidth=5,
            markersize=10
        )

        for i, p in enumerate(points):
            self.ax.text(
                p[0],
                p[1]+2,
                f"J{i}"
            )

        self.ax.set_title(
            "Soft Prosthetic Finger Simulator"
        )

        self.ax.set_xlim(-30,120)
        self.ax.set_ylim(-30,120)

        self.ax.set_aspect("equal")

        self.ax.grid(True)

        self.fig.canvas.draw_idle()


