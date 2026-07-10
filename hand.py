# hand.py
from finger import Finger

class Hand:
    def __init__(self):
        self.fingers = [
            # Shortened the thumb segments to look realistic
            Finger("Thumb", 22, 16, 0),  # Third segment is set to 0 length
            Finger("Index", 48, 28, 18),
            Finger("Middle", 54, 32, 20),
            Finger("Ring", 48, 30, 18),
            Finger("Pinky", 40, 24, 16)
        ]

    def get_finger(self, name):
        for finger in self.fingers:
            if finger.name == name:
                return finger
        return None

    def open_hand(self):
        for finger in self.fingers:
            finger.set_angles(0, 0, 0)

    def fist(self):
        # Thumb curls across with its two joints; fingers curl with three
        self.get_finger("Thumb").set_angles(55, 60, 0)
        self.get_finger("Index").set_angles(65, 90, 70)
        self.get_finger("Middle").set_angles(65, 90, 70)
        self.get_finger("Ring").set_angles(65, 90, 70)
        self.get_finger("Pinky").set_angles(65, 90, 70)

    def pinch(self):
        self.open_hand()
        self.get_finger("Thumb").set_angles(35, 45, 0)
        self.get_finger("Index").set_angles(40, 60, 35)

    def tripod(self):
        self.open_hand()
        self.get_finger("Thumb").set_angles(35, 45, 0)
        self.get_finger("Index").set_angles(45, 60, 30)
        self.get_finger("Middle").set_angles(45, 60, 30)


