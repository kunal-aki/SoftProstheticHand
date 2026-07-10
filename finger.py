# finger.py
class Finger:
    def __init__(self, name, proximal_length, middle_length, distal_length):
        self.name = name
        self.proximal_length = proximal_length
        self.middle_length = middle_length
        self.distal_length = distal_length
        
        # Track angles dynamically
        self.mcp_angle = 0.0
        self.pip_angle = 0.0
        self.dip_angle = 0.0

    def set_angles(self, mcp, pip, dip):
        self.mcp_angle = mcp
        self.pip_angle = pip
        self.dip_angle = dip


