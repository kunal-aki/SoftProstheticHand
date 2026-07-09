class Finger:
    def __init__(
        self,
        name,
        proximal_length,
        middle_length,
        distal_length
    ):
        self.name = name

        # Bone lengths (mm)
        self.proximal_length = proximal_length
        self.middle_length = middle_length
        self.distal_length = distal_length

        # Joint angles (degrees)
        self.mcp_angle = 0
        self.pip_angle = 0
        self.dip_angle = 0

    def set_angles(self, mcp, pip, dip):
        self.mcp_angle = mcp
        self.pip_angle = pip
        self.dip_angle = dip

    def get_angles(self):
        return (
            self.mcp_angle,
            self.pip_angle,
            self.dip_angle
        )

    def print_info(self):
        print(f"\n{self.name}")
        print("-" * 30)

        print("Segment Lengths")
        print(f"Proximal: {self.proximal_length} mm")
        print(f"Middle:    {self.middle_length} mm")
        print(f"Distal:    {self.distal_length} mm")

        print("\nJoint Angles")
        print(f"MCP: {self.mcp_angle}°")
        print(f"PIP: {self.pip_angle}°")
        print(f"DIP: {self.dip_angle}°")

