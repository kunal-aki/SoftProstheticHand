import matplotlib.pyplot as plt

from hand import Hand
from visualization import HandVisualizer


hand = Hand()

viewer = HandVisualizer()



def update():

    viewer.draw(hand)



def keyboard(event):

    if event.key == "1":

        print("Open Hand")
        hand.open_hand()


    elif event.key == "2":

        print("Fist")
        hand.fist()


    elif event.key == "3":

        print("Pinch")
        hand.pinch()


    elif event.key == "4":

        print("Tripod")
        hand.tripod()


    update()



viewer.fig.canvas.mpl_connect(
    "key_press_event",
    keyboard
)



hand.open_hand()

update()


print("""
3D Prosthetic Hand Simulator

Controls:

1 - Open Hand
2 - Fist
3 - Pinch
4 - Tripod

""")



plt.show()


