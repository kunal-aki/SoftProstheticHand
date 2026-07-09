from matplotlib.widgets import Slider


class FingerControls:

    def __init__(self, fig):

        ax_mcp = fig.add_axes([0.15,0.18,0.7,0.03])
        ax_pip = fig.add_axes([0.15,0.12,0.7,0.03])
        ax_dip = fig.add_axes([0.15,0.06,0.7,0.03])

        self.mcp = Slider(
            ax=ax_mcp,
            label="MCP",
            valmin=0,
            valmax=90,
            valinit=20
        )

        self.pip = Slider(
            ax=ax_pip,
            label="PIP",
            valmin=0,
            valmax=110,
            valinit=45
        )

        self.dip = Slider(
            ax=ax_dip,
            label="DIP",
            valmin=0,
            valmax=90,
            valinit=15
        )

