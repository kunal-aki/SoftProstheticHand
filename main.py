import matplotlib.pyplot as plt

from hand import Hand
from visualization import HandVisualizer


# Create hand model
prosthetic_hand = Hand()

# Create visualizer
visualizer = HandVisualizer()


def update_display():
    """
    Redraws the hand after changing finger positions.
    """
    visualizer.draw(prosthetic_hand)


def on_key(event):
    """
    Keyboard controls for changing grasp patterns.
    """

    if event.key == "1":
        print("Open Hand")
        prosthetic_hand.open_hand()

    elif event.key == "2":
        print("Fist")
        prosthetic_hand.fist()

    elif event.key == "3":
        print("Pinch")
        prosthetic_hand.pinch()

    elif event.key == "4":
        print("Tripod Grasp")
        prosthetic_hand.tripod()

    else:
        return

    update_display()


# Connect keyboard input to function
visualizer.fig.canvas.mpl_connect(
    "key_press_event",
    on_key
)


# Initial state
prosthetic_hand.open_hand()

update_display()


print("-----------------------------")
print("Virtual Prosthetic Hand")
print("-----------------------------")
print("Controls:")
print("1 - Open Hand")
print("2 - Fist")
print("3 - Pinch")
print("4 - Tripod")
print("-----------------------------")


plt.show()


