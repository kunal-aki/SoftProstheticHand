# main.py
import pyvista as pv
import time
import math
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import threading
from scipy.spatial.transform import Rotation

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

SMOOTH_COEFFICIENT = 4.0
last_frame_time = time.time()
selected_finger_name = None

# --- NEW MEDIAPIPE TASKS CAMERA ENGINE CONFIG ---
tracking_mode_active = False
cap = None

# --- WRIST TRACKING STATE (drives whole-hand position/orientation) ---
wrist_lock = threading.Lock()
target_wrist_rotation = np.eye(3)
target_wrist_translation = np.zeros(3)
current_wrist_rotation = np.eye(3)
current_wrist_translation = np.zeros(3)

# Build Hand Landmarker configuration targeting local binary graph file
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options, running_mode=vision.RunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.7
)
vision_hand_engine = vision.HandLandmarker.create_from_options(options)


def update_view():
    viewer.draw_hand(hand)


# --- PRESET TARGET CALCULATORS ---
def trigger_open():
    if tracking_mode_active:
        return
    print("[Preset] Shifting targets to Open...")
    for f in hand.fingers:
        actuation_mode[f.name] = "angle"
        target_angles[f.name]["mcp"] = 0.0
        target_angles[f.name]["pip"] = 0.0
        target_angles[f.name]["dip"] = 0.0


def trigger_fist():
    if tracking_mode_active:
        return
    print("[Preset] Shifting targets to Fist...")
    for f in hand.fingers:
        actuation_mode[f.name] = "angle"
    target_angles["Thumb"]["mcp"] = 55.0
    target_angles["Thumb"]["pip"] = 60.0
    target_angles["Thumb"]["dip"] = 0.0
    for name in ["Index", "Middle", "Ring", "Pinky"]:
        target_angles[name]["mcp"] = 70.0
        target_angles[name]["pip"] = 90.0
        target_angles[name]["dip"] = 63.0


def trigger_pinch():
    if tracking_mode_active:
        return
    trigger_open()
    target_angles["Thumb"]["mcp"] = 35.0
    target_angles["Thumb"]["pip"] = 45.0
    target_angles["Index"]["mcp"] = 45.0
    target_angles["Index"]["pip"] = 60.0
    target_angles["Index"]["dip"] = 42.0


def trigger_tripod():
    if tracking_mode_active:
        return
    trigger_open()
    target_angles["Thumb"]["mcp"] = 40.0
    target_angles["Thumb"]["pip"] = 50.0
    for name in ["Index", "Middle"]:
        target_angles[name]["mcp"] = 45.0
        target_angles[name]["pip"] = 60.0
        target_angles[name]["dip"] = 42.0


def trigger_cylinder():
    if tracking_mode_active:
        return
    for f in hand.fingers:
        actuation_mode[f.name] = "angle"
    target_angles["Thumb"]["mcp"] = 25.0
    target_angles["Thumb"]["pip"] = 30.0
    for name in ["Index", "Middle", "Ring", "Pinky"]:
        target_angles[name]["mcp"] = 40.0
        target_angles[name]["pip"] = 50.0
        target_angles[name]["dip"] = 35.0


def trigger_lateral():
    if tracking_mode_active:
        return
    for f in hand.fingers:
        actuation_mode[f.name] = "angle"
    for name in ["Index", "Middle", "Ring", "Pinky"]:
        target_angles[name]["mcp"] = 50.0
        target_angles[name]["pip"] = 80.0
        target_angles[name]["dip"] = 56.0
    target_angles["Thumb"]["mcp"] = 30.0
    target_angles["Thumb"]["pip"] = 20.0


def trigger_hook():
    if tracking_mode_active:
        return
    for f in hand.fingers:
        actuation_mode[f.name] = "angle"
    target_angles["Thumb"]["mcp"] = 0.0
    target_angles["Thumb"]["pip"] = 10.0
    for name in ["Index", "Middle", "Ring", "Pinky"]:
        target_angles[name]["mcp"] = 10.0
        target_angles[name]["pip"] = 85.0
        target_angles[name]["dip"] = 59.0


def select_finger(name):
    global selected_finger_name
    if tracking_mode_active:
        return
    selected_finger_name = name
    print(f"[Selection] Domain Focus: {name.upper() if name else 'WHOLE HAND'}")


def toggle_hand_model():
    """Bound to the 'L' key: swaps between a right-hand and left-hand model."""
    viewer.toggle_handedness()


# --- INPUT AND CONTROL MODIFIERS ---
def modify_joints(joint_type, direction):
    if tracking_mode_active:
        return
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
    if tracking_mode_active:
        return
    target_names = [selected_finger_name] if selected_finger_name else [f.name for f in hand.fingers]
    for name in target_names:
        actuation_mode[name] = mode
        if mode == "tendon":
            target_tendon[name] = max(0.0, target_tendon[name] + direction * 10.0)
        elif mode == "pressure":
            target_pressure[name] = max(0.0, target_pressure[name] + direction * 5.0)


# --- BACKGROUND WEBCAM COMPUTER VISION THREAD ---
def calculate_3d_joint_angle(pA, pB, pC):
    v1 = np.array(pA) - np.array(pB)
    v2 = np.array(pC) - np.array(pB)
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    cosine_angle = dot_product / (norm_v1 * norm_v2)
    angle_radians = math.acos(max(-1.0, min(1.0, cosine_angle)))
    flexion_deg = 180.0 - math.degrees(angle_radians)
    return max(0.0, flexion_deg)


def calculate_wrist_frame(points):
    """Derives a rigid rotation + translation for the whole hand from the
    wrist and finger-base ("knuckle") landmarks, so the hand model can move
    and orient itself along with the user's real wrist.

    points are (x, y, z) landmarks in MediaPipe's normalized image space:
    x/y in [0, 1] (x right, y down), z roughly the same scale, negative
    toward the camera.
    """
    # Convert to a convention matching our 3D model (x right, y up, z toward viewer)
    def conv(p):
        return np.array([p[0], -p[1], -p[2]], dtype=float)

    wrist = conv(points[0])
    index_mcp = conv(points[5])
    middle_mcp = conv(points[9])
    pinky_mcp = conv(points[17])

    # Forward axis: wrist -> middle knuckle (points "away" along the fingers)
    y_axis = middle_mcp - wrist
    y_norm = np.linalg.norm(y_axis)
    if y_norm < 1e-6:
        return None
    y_axis = y_axis / y_norm

    # Lateral reference: across the knuckles (pinky -> index)
    lateral_ref = index_mcp - pinky_mcp
    z_axis = np.cross(lateral_ref, y_axis)
    z_norm = np.linalg.norm(z_axis)
    if z_norm < 1e-6:
        return None
    z_axis = z_axis / z_norm

    x_axis = np.cross(y_axis, z_axis)
    x_axis = x_axis / (np.linalg.norm(x_axis) + 1e-8)

    rotation_matrix = np.column_stack([x_axis, y_axis, z_axis])

    # Raw landmark (pre-conversion) used for translation, mapped from
    # normalized image space into the model's world-unit scale.
    raw_wrist = points[0]
    translation = np.array([
        (raw_wrist[0] - 0.5) * 250.0,
        -(raw_wrist[1] - 0.5) * 250.0,
        -raw_wrist[2] * 400.0
    ])

    return rotation_matrix, translation


def webcam_vision_worker():
    global tracking_mode_active, cap, target_angles
    global target_wrist_rotation, target_wrist_translation

    finger_landmarks = {
        "Index": {"mcp": (0, 5, 6), "pip": (5, 6, 7), "dip": (6, 7, 8)},
        "Middle": {"mcp": (0, 9, 10), "pip": (9, 10, 11), "dip": (10, 11, 12)},
        "Ring": {"mcp": (0, 13, 14), "pip": (13, 14, 15), "dip": (14, 15, 16)},
        "Pinky": {"mcp": (0, 17, 18), "pip": (17, 18, 19), "dip": (18, 19, 20)},
        "Thumb": {"mcp": (0, 1, 2), "pip": (1, 2, 3), "dip": (2, 3, 4)}
    }

    while True:
        if tracking_mode_active:
            if cap is None or not cap.isOpened():
                cap = cv2.VideoCapture(0)
                time.sleep(0.5)
                continue

            success, frame = cap.read()
            if not success:
                continue

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Wrap image into modern MediaPipe Tasks layout container
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            results = vision_hand_engine.detect(mp_image)

            if results.hand_landmarks:
                hand_lms = results.hand_landmarks[0]
                points = [(lm.x, lm.y, lm.z) for lm in hand_lms]

                for f_name, joints in finger_landmarks.items():
                    actuation_mode[f_name] = "angle"

                    mcp_ang = calculate_3d_joint_angle(
                        points[joints["mcp"][0]], points[joints["mcp"][1]], points[joints["mcp"][2]])
                    pip_ang = calculate_3d_joint_angle(
                        points[joints["pip"][0]], points[joints["pip"][1]], points[joints["pip"][2]])
                    dip_ang = calculate_3d_joint_angle(
                        points[joints["dip"][0]], points[joints["dip"][1]], points[joints["dip"][2]])

                    if f_name == "Thumb":
                        target_angles[f_name]["mcp"] = min(55.0, mcp_ang * 2.0)
                        target_angles[f_name]["pip"] = min(60.0, pip_ang * 1.8)
                        target_angles[f_name]["dip"] = 0.0
                    else:
                        target_angles[f_name]["mcp"] = min(90.0, mcp_ang * 2.2)
                        target_angles[f_name]["pip"] = min(110.0, pip_ang * 2.0)
                        target_angles[f_name]["dip"] = 0.7 * target_angles[f_name]["pip"]

                # Whole-hand movement: derive wrist position/orientation from
                # the landmarks so the 3D hand tracks the user's real wrist.
                wrist_frame = calculate_wrist_frame(points)
                if wrist_frame is not None:
                    rotation_matrix, translation = wrist_frame
                    with wrist_lock:
                        target_wrist_rotation = rotation_matrix
                        target_wrist_translation = translation

            cv2.putText(frame, "LIVE HAND TRACKING ACTIVE (V TO EXIT)",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.imshow("Webcam Calibration Feed", frame)
            cv2.waitKey(1)
        else:
            if cap is not None:
                cap.release()
                cap = None
                cv2.destroyAllWindows()
            time.sleep(0.2)


def toggle_hand_tracking():
    global tracking_mode_active, target_wrist_rotation, target_wrist_translation
    tracking_mode_active = not tracking_mode_active
    print(f"[Mode Switch] Camera Hand Tracking Status: {tracking_mode_active}")
    if not tracking_mode_active:
        trigger_open()
        with wrist_lock:
            target_wrist_rotation = np.eye(3)
            target_wrist_translation = np.zeros(3)


vision_thread = threading.Thread(target=webcam_vision_worker, daemon=True)
vision_thread.start()


# --- MASTER STEP TIME-LOOP MECHANISM ---
def animation_step_callback():
    global last_frame_time, current_wrist_rotation, current_wrist_translation

    current_time = time.time()
    dt = current_time - last_frame_time
    last_frame_time = current_time
    dt = min(dt, 0.1)

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

    # --- Smoothly track the target wrist rotation/translation ---
    with wrist_lock:
        t_rotation = target_wrist_rotation.copy()
        t_translation = target_wrist_translation.copy()

    cur_quat = Rotation.from_matrix(current_wrist_rotation).as_quat()
    tgt_quat = Rotation.from_matrix(t_rotation).as_quat()
    if np.dot(cur_quat, tgt_quat) < 0:
        tgt_quat = -tgt_quat
    new_quat = cur_quat + (tgt_quat - cur_quat) * lerp_factor
    new_quat_norm = np.linalg.norm(new_quat)
    if new_quat_norm > 1e-8:
        new_quat = new_quat / new_quat_norm
        current_wrist_rotation = Rotation.from_quat(new_quat).as_matrix()

    current_wrist_translation = current_wrist_translation + (t_translation - current_wrist_translation) * lerp_factor

    viewer.set_wrist_transform(current_wrist_rotation, current_wrist_translation)

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

viewer.plotter.add_key_event("v", toggle_hand_tracking)
viewer.plotter.add_key_event("l", toggle_hand_model)

trigger_open()
update_view()

viewer.plotter.iren.initialize()
viewer.plotter.add_timer_event(max_steps=10000000, duration=16,
                                callback=lambda step: animation_step_callback())
viewer.plotter.show()



