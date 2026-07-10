# visualization.py
import pyvista as pv
import numpy as np
from kinematics import forward_kinematics_3d

class HandVisualizer3D:
    def __init__(self):
        self.plotter = pv.Plotter()
        self.plotter.set_background("#eceff1")
        
        self.bases = [
            (-26, -8, 6),   # Thumb
            (-16, 22, 0),   # Index
            (0, 25, 1),     # Middle
            (16, 21, 0),    # Ring
            (28, 14, -2)    # Pinky
        ]
        
        self.skin_color = "#e0a98c"
        self.joint_color = "#b07d62"
        
        self.bone_actors = []
        self.joint_actors = []
        self.initialized = False

    def create_bone(self, start, end, radius_start, radius_end):
        start = np.array(start)
        end = np.array(end)
        center = (start + end) / 2
        direction = end - start
        height = np.linalg.norm(direction)
        
        if height < 1e-5:
            return pv.Sphere(radius=radius_start, center=start)

        return pv.CylinderStructured(
            center=center,
            direction=direction,
            radius=[radius_start, radius_end],
            height=height
        )

    def draw_hand(self, hand):
        if not self.initialized:
            palm_points = np.array([
                [-16, -30, -6], [16, -30, -6],
                [-16, -30,  4], [16, -30,  4],
                [-32,  12, -6], [32,   8, -8],
                [-32,  12,  6], [32,   8,  4],
                [-26,  -8,  6]
            ])
            palm = pv.PolyData(palm_points).delaunay_3d().extract_surface().smooth(n_iter=20)
            self.plotter.add_mesh(palm, color=self.skin_color, opacity=0.9, roughness=0.6, pickable=False)

            instructions = (
                "PROSTHETIC HAND SIMULATOR\n\n"
                "Preset Poses:\n"
                "  1: Open Hand\n"
                "  2: Full Fist\n"
                "  3: Tip Pinch\n"
                "  4: Tripod Grasp\n\n"
                "Manual Adjustments:\n"
                "  Q / A : Flex / Extend MCP\n"
                "  W / S : Flex / Extend PIP\n"
                "  E / D : Flex / Extend DIP\n\n"
                "Click & drag background to rotate view."
            )
            self.plotter.add_text(instructions, position="upper_left", font_size=10, color="black")

        bone_idx = 0
        joint_idx = 0

        for index, finger in enumerate(hand.fingers):
            joints = forward_kinematics_3d(finger, self.bases[index])

            # Update Bones dynamically based on how many segments this finger has
            for i in range(len(joints) - 1):
                # Apply anatomical tapering rules
                if finger.name == "Thumb":
                    r_start = 5.0 if i == 0 else 3.8
                    r_end = 3.8 if i == 0 else 2.4
                else:
                    r_start = 4.2 if i == 0 else (3.2 if i == 1 else 2.5)
                    r_end = 3.2 if i == 0 else (2.5 if i == 1 else 1.8)

                mesh = self.create_bone(joints[i], joints[i+1], r_start, r_end)
                
                if not self.initialized:
                    actor = self.plotter.add_mesh(mesh, color=self.skin_color, roughness=0.5)
                    self.bone_actors.append(actor)
                else:
                    self.bone_actors[bone_idx].mapper.SetInputData(mesh)
                bone_idx += 1

            # Update Knuckle Spheres dynamically
            for i, joint in enumerate(joints):
                if finger.name == "Thumb":
                    rad = 5.5 if i == 0 else (4.2 if i == 1 else 3.0)
                else:
                    rad = 5.0 if i == 0 else (3.8 if i == 1 else 2.8)
                    
                mesh = pv.Sphere(radius=rad, center=joint)
                
                if not self.initialized:
                    actor = self.plotter.add_mesh(mesh, color=self.joint_color, roughness=0.4)
                    self.joint_actors.append(actor)
                else:
                    self.joint_actors[joint_idx].mapper.SetInputData(mesh)
                joint_idx += 1
                
        self.initialized = True
        self.plotter.render()


