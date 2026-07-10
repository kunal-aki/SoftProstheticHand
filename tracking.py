import cv2
import mediapipe as mp

class HandTracker:

    def __init__(self):

        self.mpHands = mp.solutions.hands

        self.hands = self.mpHands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )

        self.draw = mp.solutions.drawing_utils

    def get_landmarks(self, frame):

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = self.hands.process(rgb)

        landmark_list = []

        if results.multi_hand_landmarks:

            hand = results.multi_hand_landmarks[0]

            self.draw.draw_landmarks(
                frame,
                hand,
                self.mpHands.HAND_CONNECTIONS
            )

            h, w, _ = frame.shape

            for lm in hand.landmark:

                landmark_list.append(
                    (
                        lm.x * w,
                        lm.y * h,
                        lm.z
                    )
                )

        return frame, landmark_list

