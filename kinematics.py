import numpy as np
from scipy.spatial.transform import Rotation


def create_rotation(rx, ry, rz):
    """
    Creates a 3D rotation matrix
    """

    return Rotation.from_euler(
        "xyz",
        [rx, ry, rz],
        degrees=True
    ).as_matrix()



def forward_kinematics_3d(finger, base_position):

    joints = []

    current_position = np.array(base_position)

    joints.append(current_position.copy())


    # Initial finger direction
    direction = np.array([0,0,1])


    # MCP rotation
    R1 = create_rotation(
        0,
        finger.mcp_angle,
        0
    )

    direction = R1 @ direction

    current_position = (
        current_position
        +
        direction * finger.proximal_length
    )

    joints.append(current_position.copy())


    # PIP rotation

    R2 = create_rotation(
        0,
        finger.pip_angle,
        0
    )

    direction = R2 @ direction


    current_position = (
        current_position
        +
        direction * finger.middle_length
    )

    joints.append(current_position.copy())


    # DIP rotation

    R3 = create_rotation(
        0,
        finger.dip_angle,
        0
    )

    direction = R3 @ direction


    current_position = (
        current_position
        +
        direction * finger.distal_length
    )

    joints.append(current_position.copy())


    return joints


