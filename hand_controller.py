import bpy
import math


# -----------------------------
# SETTINGS
# -----------------------------

ARMATURE_NAME = "Hand_Armature"


# Current selected finger

selected_finger = "index"


# Finger joint mapping

finger_joints = {

    "thumb": [
        "thumb_CMC",
        "thumb_MCP",
        "thumb_IP"
    ],

    "index": [
        "index_MCP",
        "index_PIP",
        "index_DIP"
    ],

    "middle": [
        "middle_MCP",
        "middle_PIP",
        "middle_DIP"
    ],

    "ring": [
        "ring_MCP",
        "ring_PIP",
        "ring_DIP"
    ],

    "pinky": [
        "pinky_MCP",
        "pinky_PIP",
        "pinky_DIP"
    ]

}



# -----------------------------
# ROTATE JOINT
# -----------------------------

def rotate_joint(
        bone_name,
        angle
):

    armature = bpy.data.objects[ARMATURE_NAME]


    bone = (
        armature
        .pose
        .bones
        .get(bone_name)
    )


    if bone:

        bone.rotation_mode = "XYZ"


        # Convert degrees

        bone.rotation_euler[0] = math.radians(angle)



# -----------------------------
# CONTROL FINGER
# -----------------------------

def move_finger(
        finger,
        MCP,
        PIP,
        DIP
):

    joints = finger_joints[finger]


    rotate_joint(
        joints[0],
        MCP
    )

    rotate_joint(
        joints[1],
        PIP
    )

    rotate_joint(
        joints[2],
        DIP
    )



# -----------------------------
# PRESET GRASPS
# -----------------------------

def open_hand():

    for finger in finger_joints:

        move_finger(
            finger,
            0,
            0,
            0
        )



def fist():

    for finger in finger_joints:

        move_finger(
            finger,
            70,
            90,
            70
        )



def pinch():

    open_hand()


    move_finger(
        "index",
        50,
        80,
        50
    )


    move_finger(
        "thumb",
        40,
        50,
        30
    )



# -----------------------------
# RUN
# -----------------------------


open_hand()

print(
"""
Anatomical Hand Controller Loaded

Functions:

open_hand()
fist()
pinch()

Example:

move_finger(
    "index",
    45,
    60,
    30
)

"""
)

