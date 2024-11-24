# Enhanced Look-Ahead Lateral Control in Autonomous Vehicles
Overview
This repository contains the implementation of a novel control strategy for autonomous vehicles, combining Inverse Perspective Mapping (IPM) with Inertial Measurement Unit (IMU) data to dynamically adjust the region of interest (ROI) for improved look-ahead lateral control. The project focuses on addressing challenges posed by road slopes, curvatures, and surface irregularities, ensuring robust lane detection and vehicle stability.

Key Features
Inverse Perspective Mapping (IPM): Converts road images into a bird's-eye view for enhanced lane feature extraction.
IMU Integration: Dynamically adjusts ROI using pitch and roll data for real-time adaptation to road conditions.
Look-Ahead PID Controller: Predicts trajectories and computes steering adjustments for smooth lane-keeping.
Simulation in CARLA: Tested in realistic simulated environments with diverse road conditions.
Real-World Validation: Implemented on a test vehicle equipped with a camera and MPU9250 IMU sensor.

<img width="810" alt="Screenshot 2024-11-24 145548" src="https://github.com/user-attachments/assets/fb7096af-78a9-4d09-9033-9f1f9188451c">
