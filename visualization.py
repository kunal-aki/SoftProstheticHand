import pyvista as pv
import numpy as np

from kinematics import forward_kinematics_3d



class HandVisualizer3D:


    def __init__(self):

        self.plotter = pv.Plotter()

        self.plotter.set_background(
            "white"
        )


    def create_bone(
        self,
        start,
        end,
        radius=3
    ):

        start=np.array(start)
        end=np.array(end)


        center = (start+end)/2

        length=np.linalg.norm(
            end-start
        )


        cylinder = pv.Cylinder(
            center=center,
            direction=end-start,
            radius=radius,
            height=length
        )


        return cylinder



    def draw_hand(self, hand):


        colors=[
            "orange",
            "red",
            "green",
            "blue",
            "purple"
        ]


        bases=[

            (-40,0,0),
            (-20,0,0),
            (0,0,0),
            (20,0,0),
            (40,0,0)

        ]


        # Palm

        palm = pv.Box(
            bounds=(-50,50,-20,20,-10,10)
        )

        self.plotter.add_mesh(
            palm,
            color="tan"
        )



        for index,finger in enumerate(hand.fingers):


            joints = forward_kinematics_3d(
                finger,
                bases[index]
            )


            # Bones

            for i in range(len(joints)-1):

                bone=self.create_bone(
                    joints[i],
                    joints[i+1]
                )


                self.plotter.add_mesh(
                    bone,
                    color=colors[index]
                )


            # Joints

            for joint in joints:

                sphere=pv.Sphere(
                    radius=5,
                    center=joint
                )

                self.plotter.add_mesh(
                    sphere,
                    color="black"
                )


        self.plotter.show()


