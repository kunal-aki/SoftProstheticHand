# hand.py
from finger import Finger


class Hand:
    def __init__(self):
        self.fingers = [
            Finger("Thumb", 22, 16, 0, joint_stiffness=0.25),
            Finger("Index", 48, 28, 18, joint_stiffness=0.15),
            Finger("Middle", 54, 32, 20, joint_stiffness=0.16),
            Finger("Ring", 48, 30, 18, joint_stiffness=0.14),
            Finger("Pinky", 40, 24, 16, joint_stiffness=0.12)
        ]

    def get_finger(self, name):
        for finger in self.fingers:
            if finger.name == name:
                return finger
        return None

    # --- SIMULATOR GRASP LIBRARY PRESETS ---
    def open_hand(self):
        for finger in self.fingers:
            finger.set_angles(0, 0, 0)

    def fist(self):
        self.get_finger("Thumb").set_angles(55, 60, 0)
        for name in ["Index", "Middle", "Ring", "Pinky"]:
            # Coupling defaults automatically active via angle clamping inputs
            self.get_finger(name).set_angles(70, 90, 63)  # 63 is 0.7 * 90

    def pinch(self):
        self.open_hand()
        self.get_finger("Thumb").set_angles(35, 45, 0)
        self.get_finger("Index").set_angles(45, 60, 42)

    def tripod(self):
        self.open_hand()
        self.get_finger("Thumb").set_angles(40, 50, 0)
        for name in ["Index", "Middle"]:
            self.get_finger(name).set_angles(45, 60, 42)

    def cylindrical_grasp(self):
        """Large diameter object hold (e.g., soda can or bottle hold)"""
        self.get_finger("Thumb").set_angles(25, 30, 0)
        for name in ["Index", "Middle", "Ring", "Pinky"]:
            self.get_finger(name).set_angles(40, 50, 35)

    def lateral_key_grip(self):
        """Thumb clamping flatly against the side profile of the flexed Index finger."""
        for name in ["Index", "Middle", "Ring", "Pinky"]:
            self.get_finger(name).set_angles(50, 80, 56)
        self.get_finger("Thumb").set_angles(30, 20, 0)

    def hook_grip(self):
        """Carrying a handle weight: Knuckles flat, middle joints curved."""
        self.get_finger("Thumb").set_angles(0, 10, 0)
        for name in ["Index", "Middle", "Ring", "Pinky"]:
            self.get_finger(name).set_angles(10, 85, 59)



