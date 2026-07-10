import math


def forward_kinematics_3d(finger, base=(0, 0, 0)):
    """
    Calculates 3D joint positions for a finger.

    Returns:
        [
        (base),
        (MCP),
        (PIP),
        (DIP/tip)
        ]
    """

    x0, y0, z0 = base

    # Convert degrees to radians
    theta1 = math.radians(finger.mcp_angle)
    theta2 = math.radians(finger.pip_angle)
    theta3 = math.radians(finger.dip_angle)

    # MCP rotation
    x1 = x0 + finger.proximal_length * math.cos(theta1)
    y1 = y0
    z1 = z0 + finger.proximal_length * math.sin(theta1)


    # PIP rotation
    x2 = x1 + finger.middle_length * math.cos(theta1 + theta2)
    y2 = y1
    z2 = z1 + finger.middle_length * math.sin(theta1 + theta2)


    # DIP rotation
    x3 = x2 + finger.distal_length * math.cos(theta1 + theta2 + theta3)
    y3 = y2
    z3 = z2 + finger.distal_length * math.sin(theta1 + theta2 + theta3)


    return [
        (x0, y0, z0),
        (x1, y1, z1),
        (x2, y2, z2),
        (x3, y3, z3)
    ]


