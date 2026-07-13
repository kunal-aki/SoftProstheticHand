# finger.py
class Finger:
    def __init__(self, name, proximal_length, middle_length,
                 distal_length, joint_stiffness=0.15):
        self.name = name
        self.proximal_length = proximal_length
        self.middle_length = middle_length
        self.distal_length = distal_length

        # Biomechanical Joint Limits (Flexion max bounds in degrees)
        self.limits = {
            "mcp": (0.0, 90.0),
            "pip": (0.0, 110.0),
            "dip": (0.0, 80.0)
        }

        # Dynamic State Variables
        self.mcp_angle = 0.0
        self.pip_angle = 0.0
        self.dip_angle = 0.0

        # Engineering Dashboard Outputs
        self.tendon_tension = 0.0       # Simulated force in Newtons (N)
        self.actuator_pressure = 0.0    # Simulated Soft Actuator pressure in kPa
        self.joint_stiffness = joint_stiffness  # Rotational spring constant (Nm/deg)
        self.estimated_torque = 0.0     # Torque load computed at the base MCP joint (Nm)

    def set_angles(self, mcp, pip, dip):
        """Enforces physical structural bounds and updates mechanical state."""
        self.mcp_angle = max(self.limits["mcp"][0], min(self.limits["mcp"][1], mcp))
        self.pip_angle = max(self.limits["pip"][0], min(self.limits["pip"][1], pip))
        self.dip_angle = max(self.limits["dip"][0], min(self.limits["dip"][1], dip))

    def update_from_tendon_force(self, force_newtons):
        """Phase 1: Calculates biomechanical angles derived from linear tendon force."""
        self.tendon_tension = max(0.0, force_newtons)
        moment_arm = 0.012  # 12mm anatomical joint radius

        self.estimated_torque = self.tendon_tension * moment_arm
        calculated_mcp = self.estimated_torque / self.joint_stiffness
        calculated_pip = calculated_mcp * 1.2

        if self.name != "Thumb":
            calculated_dip = 0.7 * calculated_pip
        else:
            calculated_dip = 0.0
        self.set_angles(calculated_mcp, calculated_pip, calculated_dip)

    def update_from_pressure(self, pressure_kpa):
        """Phase 2: Calculates constant curvature bending based on internal pneumatic pressure."""
        self.actuator_pressure = max(0.0, pressure_kpa)
        expansion_coefficient = 0.65
        calculated_mcp = self.actuator_pressure * expansion_coefficient
        calculated_pip = calculated_mcp * 1.1

        if self.name != "Thumb":
            calculated_dip = 0.7 * calculated_pip
        else:
            calculated_dip = 0.0

        self.estimated_torque = (calculated_mcp * self.joint_stiffness) * 0.8
        self.tendon_tension = self.estimated_torque / 0.012

        self.set_angles(calculated_mcp, calculated_pip, calculated_dip)



