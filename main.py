from hand import Hand
from visualization import HandVisualizer3D


hand = Hand()


# Start with open hand

hand.open_hand()


# Create viewer

viewer = HandVisualizer3D()


viewer.draw_hand(
    hand
)


