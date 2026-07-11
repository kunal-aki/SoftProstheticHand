# visualization.py
import pyvista as pv
import numpy as np
from kinematics import forward_kinematics_3d

class HandVisualizer3D:
    def __init__(self):
        self.plotter = pv.Plotter()
        self.plotter.set_background("#eceff1") 
        
        self.bases = [
            (-26, -8, 6), (-16, 22, 0), (0, 25, 1), (16, 21, 0), (28, 14, -2)
        ]
        
        self.skin_color = "#e0a98c"
        self.joint_color = "#b07d62"
        self.bone_actors = []
        self.joint_actors = []
        self.initialized = False
        self.telemetry_actor = None

    def create_bone(self, start, end, radius_start, radius_end):
        start = np.array(start)
        end = np.array(end)
        center = (start + end) / 2
        direction = end - start
        height = np.linalg.norm(direction)
        if height < 1e-5:
            return pv.Sphere(radius=radius_start, center=start)
        return pv.CylinderStructured(center=center, direction=direction, radius=[radius_start, radius_end], height=height)

    def draw_hand(self, hand):
        if not self.initialized:
            palm_points = np.array([
                [-16, -30, -6], [16, -30, -6], [-16, -30, 4], [16, -30, 4],
                [-32, 12, -6], [32, 8, -8], [-32, 12, 6], [32, 8, 4], [-26, -8, 6]
            ])
            palm = pv.PolyData(palm_points).delaunay_3d().extract_surface().smooth(n_iter=20)
            self.plotter.add_mesh(palm, color=self.skin_color, opacity=0.9, roughness=0.6, pickable=False)

            # Clean Static Dashboard Menu Text
            menu_text = (
                " [ SELECTION INDEX ]                "
                " [ ACTUATION BENDS ]               "
                " [ HARDWARE PRESETS ]\n"
                "  F: Thumb    G: Index                Z/A: Knuckle Flex (MCP)          1: Open   2: Fist\n"
                "  H: Middle   J: Ring                 X/S: Mid Joint Flex (PIP)        3: Pinch  4: Tripod\n"
                "  K: Pinky    SPACE: All              C/D: Tip Flex (DIP / Coupled)    5: Cylinder 6: Lateral 7: Hook"
            )
            self.plotter.add_text(menu_text, position=(0.02, 0.88), font_size=9, color="black", font="courier", viewport=True)

            # Initialize the text slot allocation once to fix bottom flickering issues completely
            self.telemetry_actor = self.plotter.add_text(
                "", position=(0.02, 0.02), font_size=9, color="#1a237e", font="courier", viewport=True
            )

        # Re-build telemetry visual readout data string
        telemetry_lines = ["\n[ VIRTUAL PROSTHETIC TELEMETRY DATA ]"]
        for f in hand.fingers:
            telemetry_lines.append(
                f"  {f.name:<6} -> Angles:[{int(f.mcp_angle):>2}°, {int(f.pip_angle):>2}°, {int(f.dip_angle):>2}°] | "
                
            )
        
        # Modify the existing actor string in place to stop flickering
        self.telemetry_actor.SetInput("\n".join(telemetry_lines))

        bone_idx = 0
        joint_idx = 0

        for index, finger in enumerate(hand.fingers):
            joints = forward_kinematics_3d(finger, self.bases[index])

            for i in range(len(joints) - 1):
                if finger.name == "Thumb":
                    r_start, r_end = 5.0, 3.8 if i == 0 else 2.4
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

            for i, joint in enumerate(joints):
                rad = 5.5 if finger.name == "Thumb" else 5.0
                if i > 0: rad *= 0.75
                mesh = pv.Sphere(radius=rad, center=joint)
                if not self.initialized:
                    actor = self.plotter.add_mesh(mesh, color=self.joint_color, roughness=0.4)
                    self.joint_actors.append(actor)
                else:
                    self.joint_actors[joint_idx].mapper.SetInputData(mesh)
                joint_idx += 1
                
        self.initialized = True
        self.plotter.render()


