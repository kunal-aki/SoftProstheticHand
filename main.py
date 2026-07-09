import matplotlib.pyplot as plt

from finger import Finger
from kinematics import forward_kinematics
from visualization import FingerVisualizer
from ui import FingerControls


finger = Finger(
    "Index Finger",
    50,
    30,
    20
)

viewer = FingerVisualizer()

controls = FingerControls(viewer.fig)


def update(val):

    finger.set_angles(
        controls.mcp.val,
        controls.pip.val,
        controls.dip.val
    )

    points = forward_kinematics(finger)

    viewer.draw(points)


controls.mcp.on_changed(update)
controls.pip.on_changed(update)
controls.dip.on_changed(update)

update(None)

plt.show()


