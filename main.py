# main.py
import pyvista as pv
from hand import Hand
from visualization import HandVisualizer3D

# Instantiate data and visual mechanics classes
hand = Hand()
viewer = HandVisualizer3D()

def update_view():
    viewer.draw_hand(hand)

# Wrap commands as explicit callback parameters (PyVista requires no argument functions here)
def trigger_open():
    print("Action: Open Hand")
    hand.open_hand()
    update_view()

def trigger_fist():
    print("Action: Fist")
    hand.fist()
    update_view()

def trigger_pinch():
    print("Action: Pinch")
    hand.pinch()
    update_view()

def trigger_tripod():
    print("Action: Tripod")
    hand.tripod()
    update_view()

# Hook callbacks straight into PyVista UI framework
viewer.plotter.add_key_event("1", trigger_open)
viewer.plotter.add_key_event("2", trigger_fist)
viewer.plotter.add_key_event("3", trigger_pinch)
viewer.plotter.add_key_event("4", trigger_tripod)

# Run default posture visualization setup
hand.open_hand()
update_view()

print("""
===========================================
3D Prosthetic Hand Simulator Active
===========================================
Click inside the PyVista window, then press:

  1 -> Open Hand
  2 -> Fist
  3 -> Pinch
  4 -> Tripod
===========================================
""")

# Start the interactive UI display window
viewer.plotter.show()


