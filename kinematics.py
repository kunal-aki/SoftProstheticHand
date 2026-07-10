# kinematics.py
import numpy as np
from scipy.spatial.transform import Rotation

def create_rotation_matrix(axis, angle_degrees):
    """Creates a 3D rotation matrix around a specific custom axis vector."""
    axis = axis / np.linalg.norm(axis)
    rad = np.radians(angle_degrees)
    return Rotation.from_rotvec(rad * axis).as_matrix()

def forward_kinematics_3d(finger, base_position):
    joints = []
    current_position = np.array(base_position, dtype=float)
    joints.append(current_position.copy())

    # Establish natural, anatomically splayed resting directions
    if finger.name == "Thumb":
        # Pointing outward to the side (-X) and slightly forward (+Z)
        direction = np.array([-0.8, 0.4, 0.4])
        # The thumb rotates around an axis that sweeps it ACROSS the palm
        rotation_axis = np.array([0.3, 0.8, -0.5])
    else:
        # Fingers point upward (+Y) with natural horizontal splay
        rotation_axis = np.array([1.0, 0.0, 0.0]) # Standard finger curl axis (X-axis)
        if finger.name == "Index":   direction = np.array([-0.08, 0.99, 0.0])
        elif finger.name == "Middle": direction = np.array([0.0, 1.0, 0.0])
        elif finger.name == "Ring":   direction = np.array([0.08, 0.99, 0.0])
        elif finger.name == "Pinky":  direction = np.array([0.20, 0.98, 0.0])
        
    direction = direction / np.linalg.norm(direction)

    # 1. MCP / CMC Joint
    R1 = create_rotation_matrix(rotation_axis, finger.mcp_angle)
    direction = R1 @ direction
    current_position += direction * finger.proximal_length
    joints.append(current_position.copy())

    # 2. PIP / MCP Joint
    R2 = create_rotation_matrix(rotation_axis, finger.pip_angle)
    direction = R2 @ direction
    current_position += direction * finger.middle_length
    joints.append(current_position.copy())

    # 3. DIP / IP Joint
    R3 = create_rotation_matrix(rotation_axis, finger.dip_angle)
    direction = R3 @ direction
    current_position += direction * finger.distal_length
    joints.append(current_position.copy())

    return joints


