# Biomechanical Digital Twin Workspace

An interactive, physics-informed 3D digital twin platform for kinematic simulation and real-time computer vision tracking of a prosthetic hand assembly. Built on top of Python, **PyVista (VTK)**, and **MediaPipe**, this platform simulates forward kinematics, tendon-driven forces, soft robotic pressure actuation, and live joint-angle telemetry.

---

## Key Features

* **Real-Time Hand Tracking:** Integrates with your webcam using MediaPipe Tasks to translate human hand posture, joint flexing, and wrist orientation into the 3D model.
* **Biomechanical Modeling:** Computes live hardware telemetry, including joint angular configurations, tendon string tension (Newtons), actuator pressures (kPa), and MCP knuckle torque (Nm).
* **Workspace Architect Flipping:** Dynamically flip the prosthetic configuration between a **Left Hand** and **Right Hand** structure instantly with a single keystroke.
* **Pre-Programmed Core Grips:** Instantly test classic physical grasp configurations (Fist, Pinch, Cylinder, Lateral, Hook, Tripod, Open) via terminal macros.
* **Interactive HUD Dashboard:** Displays responsive on-screen mechanical telemetry readouts in real-time.

---

## Architecture & Project Directory

The system is split cleanly into individual modular components:

```text
├── main.py             # Main application loop, input handlers, & background webcam threads
├── visualization.py    # PyVista rendering engine, text HUD layers, and transformation math
├── hand.py             # Hand assembly class containing base offsets and side states
├── finger.py           # Individual link parameters, physics update bounds, and torque math
├── kinematics.py       # Forward kinematics matrix transforms via Euler angles
└── hand_landmarker.task # Local machine learning binary graph file for MediaPipe tracking

