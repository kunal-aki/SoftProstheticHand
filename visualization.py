# visualization.py
import pyvista as pv
import numpy as np
from kinematics import forward_kinematics_3d


class HandVisualizer3D:
    def __init__(self):
        self.plotter = pv.Plotter()
        self.plotter.set_background("#eceff1")

        # Base joint anchor points for a RIGHT hand model. The LEFT hand
        # model is simply this layout mirrored across the x-axis.
        self.bases_right = [
            (-26, -8, 6), (-16, 22, 0), (0, 25, 1), (16, 21, 0), (28, 14, -2)
        ]
        self.bases_left = [(-x, y, z) for (x, y, z) in self.bases_right]

        self.skin_color = "#e0a98c"
        self.joint_color = "#b07d62"
        self.bone_actors = []
        self.joint_actors = []
        self.initialized = False
        self.telemetry_actor = None
        self.palm_actor = None

        # "Right" or "Left" -- toggled live with the "L" key
        self.handedness = "Right"
        self._needs_palm_rebuild = True

        # Root (wrist) rigid-body transform applied to the whole hand.
        # Pivot is roughly the center of the palm base so rotations feel
        # like they're happening at the wrist rather than the world origin.
        self.wrist_pivot = np.array([0.0, -10.0, 0.0])
        self.wrist_rotation = np.eye(3)
        self.wrist_translation = np.zeros(3)

    def toggle_handedness(self):
        self.handedness = "Left" if self.handedness == "Right" else "Right"
        self._needs_palm_rebuild = True
        print(f"[Model Switch] Hand model set to: {self.handedness.upper()} HAND")

    def set_wrist_transform(self, rotation_matrix, translation):
        """Called every animation frame with the (smoothed) wrist orientation
        and position so the whole hand can move/rotate along with the user's
        wrist during camera tracking."""
        self.wrist_rotation = rotation_matrix
        self.wrist_translation = translation

    def _build_user_matrix(self):
        """Builds a 4x4 rigid transform: rotate about the wrist pivot, then
        translate by the tracked wrist offset."""
        R = self.wrist_rotation
        matrix = np.eye(4)
        matrix[:3, :3] = R
        matrix[:3, 3] = self.wrist_pivot + self.wrist_translation - R @ self.wrist_pivot
        return matrix

    def create_bone(self, start, end, radius_start, radius_end):
        start = np.array(start)
        end = np.array(end)
        center = (start + end) / 2
        direction = end - start
        height = np.linalg.norm(direction)
        if height < 1e-5:
            return pv.Sphere(radius=radius_start, center=start)
        return pv.CylinderStructured(center=center, direction=direction,
                                      radius=[radius_start, radius_end], height=height)

    def _rebuild_palm(self):
        if self.palm_actor is not None:
            self.plotter.remove_actor(self.palm_actor)

        palm_points = np.array([
            [-16, -30, -6], [16, -30, -6], [-16, -30, 4], [16, -30, 4],
            [-32, 12, -6], [32, 8, -8], [-32, 12, 6], [32, 8, 4],
            [-26, -8, 6]
        ])
        if self.handedness == "Left":
            palm_points = palm_points * np.array([-1.0, 1.0, 1.0])

        palm = (pv.PolyData(palm_points).delaunay_3d()
                .extract_surface().smooth(n_iter=20))
        self.palm_actor = self.plotter.add_mesh(
            palm, color=self.skin_color, opacity=0.9, roughness=0.6, pickable=False
        )
        self._needs_palm_rebuild = False

    def draw_hand(self, hand):
        mirror = (self.handedness == "Left")
        bases = self.bases_left if mirror else self.bases_right

        if not self.initialized:
            # Clean Static Dashboard Menu Text
            menu_text = (
                " [ SELECTION INDEX ]        [ ACTUATION BENDS ]                 [ HARDWARE PRESETS ]\n"
                " F: Thumb   G: Index        Z/A: Knuckle Flex (MCP)   1: Open     2: Fist\n"
                " H: Middle  J: Ring         X/S: Mid Joint Flex (PIP) 3: Pinch    4: Tripod\n"
                " K: Pinky   SPACE: All      C/D: Tip Flex (DIP/Coupled) 5: Cylinder 6: Lateral 7: Hook\n"
                " L: Switch Left/Right Hand Model     V: Toggle Live Camera Wrist/Hand Tracking"
            )
            self.plotter.add_text(menu_text, position=(0.02, 0.85),
                                   font_size=9, color="black", font="courier", viewport=True)
            # Initialize the text slot allocation once to fix bottom flickering issues completely
            self.telemetry_actor = self.plotter.add_text(
                "", position=(0.02, 0.02), font_size=9, color="#1a237e",
                font="courier", viewport=True
            )

        if self._needs_palm_rebuild:
            self._rebuild_palm()

        # Re-build telemetry visual readout data string
        telemetry_lines = [f"\n[ VIRTUAL PROSTHETIC TELEMETRY DATA ] -- {self.handedness.upper()} HAND"]
        for f in hand.fingers:
            telemetry_lines.append(
                f"  {f.name:<6} -> Angles:[{int(f.mcp_angle):>2}°, "
                f"{int(f.pip_angle):>2}°, {int(f.dip_angle):>2}°]"
            )
        # Modify the existing actor string in place to stop flickering
        self.telemetry_actor.SetInput("\n".join(telemetry_lines))

        bone_idx = 0
        joint_idx = 0
        for index, finger in enumerate(hand.fingers):
            joints = forward_kinematics_3d(finger, bases[index], mirror=mirror)

            for i in range(len(joints) - 1):
                if finger.name == "Thumb":
                    r_start, r_end = 5.0, (3.8 if i == 0 else 2.4)
                else:
                    r_start = 4.2 if i == 0 else (3.2 if i == 1 else 2.5)
                    r_end = 3.2 if i == 0 else (2.5 if i == 1 else 1.8)
                mesh = self.create_bone(joints[i], joints[i + 1], r_start, r_end)
                if not self.initialized:
                    actor = self.plotter.add_mesh(mesh, color=self.skin_color, roughness=0.5)
                    self.bone_actors.append(actor)
                else:
                    self.bone_actors[bone_idx].mapper.SetInputData(mesh)
                bone_idx += 1

            for i, joint in enumerate(joints):
                rad = 5.5 if finger.name == "Thumb" else 5.0
                if i > 0:
                    rad *= 0.75
                mesh = pv.Sphere(radius=rad, center=joint)
                if not self.initialized:
                    actor = self.plotter.add_mesh(mesh, color=self.joint_color, roughness=0.4)
                    self.joint_actors.append(actor)
                else:
                    self.joint_actors[joint_idx].mapper.SetInputData(mesh)
                joint_idx += 1

        self.initialized = True

        # Apply the current wrist transform (position + orientation) to every
        # actor that makes up the hand, so the whole hand tracks the user's
        # wrist during live camera tracking.
        user_matrix = self._build_user_matrix()
        for actor in self.bone_actors:
            actor.user_matrix = user_matrix
        for actor in self.joint_actors:
            actor.user_matrix = user_matrix
        if self.palm_actor is not None:
            self.palm_actor.user_matrix = user_matrix

        self.plotter.render()



