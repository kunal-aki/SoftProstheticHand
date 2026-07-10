import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from kinematics import forward_kinematics_3d


class HandVisualizer:


    def __init__(self):

        self.fig = plt.figure(figsize=(9,9))

        self.ax = self.fig.add_subplot(
            111,
            projection="3d"
        )


        self.base_positions = {

            "Thumb": (-30,-20,0),

            "Index": (0,0,0),

            "Middle": (20,0,0),

            "Ring": (40,0,0),

            "Pinky": (60,0,0)

        }


        self.colors = {

            "Thumb":"orange",
            "Index":"red",
            "Middle":"green",
            "Ring":"blue",
            "Pinky":"purple"

        }



    def draw(self, hand):

        self.ax.clear()


        # Palm
        palm_x = [-35,70,70,-35,-35]
        palm_y = [-20,-20,0,0,-20]
        palm_z = [0,0,0,0,0]


        self.ax.plot(
            palm_x,
            palm_y,
            palm_z,
            color="black",
            linewidth=5
        )


        for finger in hand.fingers:


            base = self.base_positions[finger.name]


            points = forward_kinematics_3d(
                finger,
                base
            )


            x = [p[0] for p in points]
            y = [p[1] for p in points]
            z = [p[2] for p in points]


            self.ax.plot(
                x,
                y,
                z,
                "-o",
                linewidth=5,
                markersize=8,
                color=self.colors[finger.name],
                label=finger.name
            )


        self.ax.set_title(
            "3D Soft Robotic Prosthetic Hand"
        )


        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.set_zlabel("Z")


        self.ax.set_xlim(-60,120)
        self.ax.set_ylim(-60,80)
        self.ax.set_zlim(-20,120)


        self.ax.legend()


        self.fig.canvas.draw_idle()


