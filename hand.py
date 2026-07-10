from finger import Finger


class Hand:

    def __init__(self):

        self.fingers = [

            Finger("Thumb",35,25,18),

            Finger("Index",50,30,20),

            Finger("Middle",55,35,22),

            Finger("Ring",50,33,20),

            Finger("Pinky",42,26,18)

        ]

    def get_finger(self, name):

        for finger in self.fingers:

            if finger.name == name:

                return finger

        return None

    def open_hand(self):

        for finger in self.fingers:

            finger.set_angles(0,0,0)

    def fist(self):

        for finger in self.fingers:

            finger.set_angles(65,90,70)

    def pinch(self):

        self.open_hand()

        self.get_finger("Thumb").set_angles(40,35,20)

        self.get_finger("Index").set_angles(40,60,35)

    def tripod(self):

        self.open_hand()

        self.get_finger("Thumb").set_angles(40,45,20)

        self.get_finger("Index").set_angles(45,60,30)

        self.get_finger("Middle").set_angles(45,60,30)

