# main.py
import pyvista as pv
import time  # Added for absolute precision delta-time tracking
from hand import Hand
from visualization import HandVisualizer3D

hand = Hand()
viewer = HandVisualizer3D()

ANGLE_STEP = 5.0  

# --- CORE ANIMATION INTERPOLATION TRACKERS ---
target_angles = {
    finger.name: {"mcp": 0.0, "pip": 0.0, "dip": 0.0}
    for finger in hand.fingers
}

target_tendon = {finger.name: 0.0 for finger in hand.fingers}
target_pressure = {finger.name: 0.0 for finger in hand.fingers}
actuation_mode = {finger.name: "angle" for finger in hand.fingers} 

# --- TIME-DELTA SMOOTHING VARIABLES ---
# A lower base coefficient creates a more natural, fluid dampening effect
SMOOTH_COEFFICIENT = 4.0  
last_frame_time = time.time()

selected_finger_name = None

def update_view():
    viewer.draw_hand(hand)

# --- PRESET TARGET CALCULATORS ---
def trigger_open():
    print("[Preset] Shifting targets to Open...")
    for f in hand.fingers:
        actuation_mode[f.name] = "angle"
        target_angles[f.name]["mcp"] = 0.0
        target_angles[f.name]["pip"] = 0.0
        target_angles[f.name]["dip"] = 0.0

def trigger_fist():
    print("[Preset] Shifting targets to Fist...")
    for f in hand.fingers: actuation_mode[f.name] = "angle"
    target_angles["Thumb"]["mcp"] = 55.0
    target_angles["Thumb"]["pip"] = 60.0
    target_angles["Thumb"]["dip"] = 0.0
    for name in ["Index", "Middle", "Ring", "Pinky"]:
        target_angles[name]["mcp"] = 70.0
        target_angles[name]["pip"] = 90.0
        target_angles[name]["dip"] = 63.0

def trigger_pinch():
    print("[Preset] Shifting targets to Pinch...")
    trigger_open()
    target_angles["Thumb"]["mcp"] = 35.0
    target_angles["Thumb"]["pip"] = 45.0
    target_angles["Index"]["mcp"] = 45.0
    target_angles["Index"]["pip"] = 60.0
    target_angles["Index"]["dip"] = 42.0

def trigger_tripod():
    print("[Preset] Shifting targets to Tripod...")
    trigger_open()
    target_angles["Thumb"]["mcp"] = 40.0
    target_angles["Thumb"]["pip"] = 50.0
    for name in ["Index", "Middle"]:
        target_angles[name]["mcp"] = 45.0
        target_angles[name]["pip"] = 60.0
        target_angles[name]["dip"] = 42.0

def trigger_cylinder():
    print("[Preset] Shifting targets to Cylinder...")
    for f in hand.fingers: actuation_mode[f.name] = "angle"
    target_angles["Thumb"]["mcp"] = 25.0
    target_angles["Thumb"]["pip"] = 30.0
    for name in ["Index", "Middle", "Ring", "Pinky"]:
        target_angles[name]["mcp"] = 40.0
        target_angles[name]["pip"] = 50.0
        target_angles[name]["dip"] = 35.0

def trigger_lateral():
    print("[Preset] Shifting targets to Lateral Grip...")
    for f in hand.fingers: actuation_mode[f.name] = "angle"
    for name in ["Index", "Middle", "Ring", "Pinky"]:
        target_angles[name]["mcp"] = 50.0
        target_angles[name]["pip"] = 80.0
        target_angles[name]["dip"] = 56.0
    target_angles["Thumb"]["mcp"] = 30.0
    target_angles["Thumb"]["pip"] = 20.0

def trigger_hook():
    print("[Preset] Shifting targets to Hook Grip...")
    for f in hand.fingers: actuation_mode[f.name] = "angle"
    target_angles["Thumb"]["mcp"] = 0.0
    target_angles["Thumb"]["pip"] = 10.0
    for name in ["Index", "Middle", "Ring", "Pinky"]:
        target_angles[name]["mcp"] = 10.0
        target_angles[name]["pip"] = 85.0
        target_angles[name]["dip"] = 59.0

def select_finger(name):
    global selected_finger_name
    selected_finger_name = name
    print(f"[Selection] Domain Focus: {name.upper() if name else 'WHOLE HAND'}")

# --- INPUT AND CONTROL MODIFIERS ---
def modify_joints(joint_type, direction):
    target_names = [selected_finger_name] if selected_finger_name else [f.name for f in hand.fingers]
    for name in target_names:
        actuation_mode[name] = "angle"
        current_target = target_angles[name][joint_type]
        
        if joint_type == "mcp":
            target_angles[name]["mcp"] = max(0.0, min(90.0, current_target + direction * ANGLE_STEP))
        elif joint_type == "pip":
            new_pip = max(0.0, min(110.0, current_target + direction * ANGLE_STEP))
            target_angles[name]["pip"] = new_pip
            if name != "Thumb":
                target_angles[name]["dip"] = 0.7 * new_pip
        elif joint_type == "dip" and name != "Thumb":
            target_angles[name]["dip"] = max(0.0, min(80.0, current_target + direction * ANGLE_STEP))

def modify_force_or_pressure(mode, direction):
    target_names = [selected_finger_name] if selected_finger_name else [f.name for f in hand.fingers]
    for name in target_names:
        actuation_mode[name] = mode
        if mode == "tendon":
            target_tendon[name] = max(0.0, target_tendon[name] + direction * 10.0)
        elif mode == "pressure":
            target_pressure[name] = max(0.0, target_pressure[name] + direction * 5.0)

# --- CINEMATIC TIME-DELTA LOOP MECHANISM ---
def animation_step_callback():
    global last_frame_time
    current_time = time.time()
    
    # Calculate how many seconds have actually passed since the last render frame
    dt = current_time - last_frame_time
    last_frame_time = current_time
    
    # Cap dt to avoid massive physics jumps if the window is dragged or frozen
    dt = min(dt, 0.1) 
    
    # Dynamic scaling factor based on real time passed
    lerp_factor = 1.0 - (2.71828 ** (-SMOOTH_COEFFICIENT * dt))

    for finger in hand.fingers:
        name = finger.name
        
        if actuation_mode[name] == "tendon":
            diff_f = target_tendon[name] - finger.tendon_tension
            finger.update_from_tendon_force(finger.tendon_tension + diff_f * lerp_factor)
            target_angles[name]["mcp"] = finger.mcp_angle
            target_angles[name]["pip"] = finger.pip_angle
            target_angles[name]["dip"] = finger.dip_angle
        elif actuation_mode[name] == "pressure":
            diff_p = target_pressure[name] - finger.actuator_pressure
            finger.update_from_pressure(finger.actuator_pressure + diff_p * lerp_factor)
            target_angles[name]["mcp"] = finger.mcp_angle
            target_angles[name]["pip"] = finger.pip_angle
            target_angles[name]["dip"] = finger.dip_angle
        else:
            finger.tendon_tension += (0.0 - finger.tendon_tension) * lerp_factor
            finger.actuator_pressure += (0.0 - finger.actuator_pressure) * lerp_factor

        curr_mcp, curr_pip, curr_dip = finger.mcp_angle, finger.pip_angle, finger.dip_angle
        
        curr_mcp += (target_angles[name]["mcp"] - curr_mcp) * lerp_factor
        curr_pip += (target_angles[name]["pip"] - curr_pip) * lerp_factor
        curr_dip += (target_angles[name]["dip"] - curr_dip) * lerp_factor
            
        finger.set_angles(curr_mcp, curr_pip, curr_dip)
    
    update_view()

# Key Bindings Mapping Setup
viewer.plotter.add_key_event("1", trigger_open)
viewer.plotter.add_key_event("2", trigger_fist)
viewer.plotter.add_key_event("3", trigger_pinch)
viewer.plotter.add_key_event("4", trigger_tripod)
viewer.plotter.add_key_event("5", trigger_cylinder)
viewer.plotter.add_key_event("6", trigger_lateral)
viewer.plotter.add_key_event("7", trigger_hook)

viewer.plotter.add_key_event("z", lambda: modify_joints("mcp", 1))   
viewer.plotter.add_key_event("a", lambda: modify_joints("mcp", -1))  
viewer.plotter.add_key_event("x", lambda: modify_joints("pip", 1))   
viewer.plotter.add_key_event("s", lambda: modify_joints("pip", -1))  
viewer.plotter.add_key_event("c", lambda: modify_joints("dip", 1))   
viewer.plotter.add_key_event("d", lambda: modify_joints("dip", -1))  

viewer.plotter.add_key_event("t", lambda: modify_force_or_pressure("tendon", 1))
viewer.plotter.add_key_event("r", lambda: modify_force_or_pressure("tendon", -1))
viewer.plotter.add_key_event("y", lambda: modify_force_or_pressure("pressure", 1))
viewer.plotter.add_key_event("e", lambda: modify_force_or_pressure("pressure", -1))

viewer.plotter.add_key_event("f", lambda: select_finger("Thumb"))
viewer.plotter.add_key_event("g", lambda: select_finger("Index"))  
viewer.plotter.add_key_event("h", lambda: select_finger("Middle")) 
viewer.plotter.add_key_event("j", lambda: select_finger("Ring"))
viewer.plotter.add_key_event("k", lambda: select_finger("Pinky"))
viewer.plotter.add_key_event("space", lambda: select_finger(None))

trigger_open()
update_view()

viewer.plotter.iren.initialize()
viewer.plotter.add_timer_event(max_steps=10000000, duration=16, callback=lambda step: animation_step_callback())
viewer.plotter.show()


