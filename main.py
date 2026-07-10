# main.py
import pyvista as pv
from hand import Hand
from visualization import HandVisualizer3D

hand = Hand()
viewer = HandVisualizer3D()

ANGLE_STEP = 5.0

def update_view():
    viewer.draw_hand(hand)

# --- PRESET HANDLERS ---
def trigger_open():
    hand.open_hand()
    update_view()

def trigger_fist():
    hand.fist()
    update_view()

def trigger_pinch():
    hand.pinch()
    update_view()

def trigger_tripod():
    hand.tripod()
    update_view()

# --- MANUAL CONTROLS ---
def modify_joints(joint_type, direction):
    for finger in hand.fingers:
        mcp, pip, dip = finger.mcp_angle, finger.pip_angle, finger.dip_angle
        if joint_type == "mcp": 
            mcp = max(0.0, min(90.0, mcp + direction * ANGLE_STEP))
        elif joint_type == "pip": 
            pip = max(0.0, min(110.0, pip + direction * ANGLE_STEP))
        elif joint_type == "dip": 
            dip = max(0.0, min(80.0, dip + direction * ANGLE_STEP))
        finger.set_angles(mcp, pip, dip)
    update_view()

# Hook Key Triggers
viewer.plotter.add_key_event("1", trigger_open)
viewer.plotter.add_key_event("2", trigger_fist)
viewer.plotter.add_key_event("3", trigger_pinch)
viewer.plotter.add_key_event("4", trigger_tripod)

# Keypress events map clean lambdas natively to the pipeline loops
viewer.plotter.add_key_event("z", lambda: modify_joints("mcp", 1))
viewer.plotter.add_key_event("a", lambda: modify_joints("mcp", -1))
viewer.plotter.add_key_event("x", lambda: modify_joints("pip", 1))
viewer.plotter.add_key_event("s", lambda: modify_joints("pip", -1))
viewer.plotter.add_key_event("c", lambda: modify_joints("dip", 1))
viewer.plotter.add_key_event("d", lambda: modify_joints("dip", -1))

# Initial baseline assembly draw
hand.open_hand()
viewer.draw_hand(hand)

print("""
===================================================
3D PROSTHETIC HAND SIMULATOR INITIALIZED (STABLE)
===================================================
1-4 : Presets
Z/A : MCP Knuckles
X/S : PIP Middle Joints
C/D : DIP Tip Joints
===================================================
""")

viewer.plotter.show()


