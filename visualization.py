# visualization.py
import pyvista as pv
import numpy as np
from kinematics import forward_kinematics_3d

class HandVisualizer3D:
    def __init__(self):
        self.plotter = pv.Plotter()
        self.plotter.set_background("#eceff1") # Soft neutral background
        
        # Real anatomical layout mapping of hand root carpals
        self.bases = [
            (-26, -8, 6),   # Thumb (Low, forward)
            (-16, 22, 0),   # Index
            (0, 25, 1),     # Middle (Highest knuckle)
            (16, 21, 0),    # Ring
            (28, 14, -2)    # Pinky (Dropped)
        ]
        
        # Human skin-tone inspired rendering colors
        self.skin_color = "#e0a98c"
        self.joint_color = "#b07d62"

    def create_bone(self, start, end, radius_start, radius_end):
        """Creates an organically tapered bone segment using a truncated cone."""
        start = np.array(start)
        end = np.array(end)
        center = (start + end) / 2
        direction = end - start
        height = np.linalg.norm(direction)
        
        if height < 1e-5:
            return pv.Sphere(radius=radius_start, center=start)

        # Build a smooth tapered cylinder (Cone/Cylinder fusion)
        bone = pv.CylinderStructured(
            center=center,
            direction=direction,
            radius=[radius_start, radius_end],
            height=height
        )
        return bone

    def draw_hand(self, hand):
        self.plotter.clear()

        # Generate a realistic fleshy palm profile mapping
        palm_points = np.array([
            [-16, -30, -6], [16, -30, -6],   # Wrist base rear
            [-16, -30,  4], [16, -30,  4],   # Wrist base front
            [-32,  12, -6], [32,   8, -8],   # Lower knuckle shelf
            [-32,  12,  6], [32,   8,  4],   # Upper knuckle shelf
            [-26,  -8,  6]                   # Thumb meat padding pad anchor
        ])
        palm = pv.PolyData(palm_points).delaunay_3d().smooth(n_iter=20)
        self.plotter.add_mesh(palm, color=self.skin_color, opacity=0.9, roughness=0.6)

        for index, finger in enumerate(hand.fingers):
            joints = forward_kinematics_3d(finger, self.bases[index])

            # Draw anatomically tapered fingers
            for i in range(len(joints) - 1):
                # Calculate tapering thicknesses
                r_start = 4.2 if i == 0 else (3.2 if i == 1 else 2.5)
                r_end = 3.2 if i == 0 else (2.5 if i == 1 else 1.8)
                
                if finger.name == "Thumb": # Thicker dimensions for the thumb
                    r_start *= 1.2
                    r_end *= 1.2

                bone = self.create_bone(joints[i], joints[i+1], r_start, r_end)
                self.plotter.add_mesh(bone, color=self.skin_color, roughness=0.5)

            # Draw smooth organic joint knuckles
            for i, joint in enumerate(joints):
                rad = 5.0 if i == 0 else (3.8 if i == 1 else 2.8)
                if finger.name == "Thumb": 
                    rad *= 1.1
                sphere = pv.Sphere(radius=rad, center=joint)
                self.plotter.add_mesh(sphere, color=self.joint_color, roughness=0.4)

        # Add explicit on-screen instructions text overlay directly into UI viewport canvas
        instructions = (
            "PROSTHETIC HAND SIMULATOR\n\n"
            "Preset Poses:\n"
            "  1: Open Hand\n"
            "  2: Full Fist\n"
            "  3: Tip Pinch\n"
            "  4: Tripod Grasp\n\n"
            "Manual Biomechanics Adjustments:\n"
            "  Q / A : Flex / Extend MCP Knuckles\n"
            "  W / S : Flex / Extend PIP Joints\n"
            "  E / D : Flex / Extend DIP Joints\n\n"
            "Click & drag background to rotate 3D view."
        )
        self.plotter.add_text(instructions, position="upper_left", font_size=10, color="black")
        self.plotter.render()


