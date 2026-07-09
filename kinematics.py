import math


def forward_kinematics(finger):
    """
    Calculates the (x, y) position of every joint
    and the fingertip.

    Returns:
        [(x0,y0), (x1,y1), (x2,y2), (x3,y3)]
    """

    # Starting point (base of finger)
    x0 = 0
    y0 = 0

    # Convert degrees to radians
    theta1 = math.radians(finger.mcp_angle)
    theta2 = math.radians(finger.pip_angle)
    theta3 = math.radians(finger.dip_angle)

    # Joint 1
    x1 = x0 + finger.proximal_length * math.cos(theta1)
    y1 = y0 + finger.proximal_length * math.sin(theta1)

    # Joint 2
    x2 = x1 + finger.middle_length * math.cos(theta1 + theta2)
    y2 = y1 + finger.middle_length * math.sin(theta1 + theta2)

    # Fingertip
    x3 = x2 + finger.distal_length * math.cos(theta1 + theta2 + theta3)
    y3 = y2 + finger.distal_length * math.sin(theta1 + theta2 + theta3)

    return [
        (x0, y0),
        (x1, y1),
        (x2, y2),
        (x3, y3)
    ]

