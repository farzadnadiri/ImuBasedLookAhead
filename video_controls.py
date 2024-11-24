import cv2
import numpy as np
from PIL import Image, ImageTk

def update_all_frames(cap, original_frame, topdown_frame, topdown_frame_imu, src_points, imu_src_points, log_func):
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Restart the video from the first frame
        ret, frame = cap.read()
    if ret:
        processed_frame1 = process_original_frame(frame.copy(), src_points, imu_src_points, log_func)
        processed_frame2 = process_topdown(frame.copy(), src_points, log_func)
        processed_frame3 = process_topdown_imu(frame.copy(), imu_src_points, log_func)
        display_frame(original_frame, processed_frame1)
        display_frame(topdown_frame, processed_frame2)
        display_frame(topdown_frame_imu, processed_frame3)
    return 0

def display_frame(label, frame):
    frame = cv2.resize(frame, (800, 600))
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_img = Image.fromarray(frame_rgb)
    frame_tk = ImageTk.PhotoImage(image=frame_img)
    label.imgtk = frame_tk
    label.config(image=frame_tk)

def process_original_frame(frame, src_points, imu_src_points, log_func):

    frame = cv2.line(frame, src_points[0], src_points[1], (0, 0, 255), 2)
    frame = cv2.line(frame, src_points[0], src_points[2], (0, 0, 255), 2)
    frame = cv2.line(frame, src_points[2], src_points[3], (0, 0, 255), 2)
    frame = cv2.line(frame, src_points[1], src_points[3], (0, 0, 255), 2)

    frame = cv2.line(frame, imu_src_points[0], imu_src_points[1], (0, 255, 0), 2)
    frame = cv2.line(frame, imu_src_points[0], imu_src_points[2], (0, 255, 0), 2)
    frame = cv2.line(frame, imu_src_points[2], imu_src_points[3], (0, 255, 0), 2)
    frame = cv2.line(frame, imu_src_points[1], imu_src_points[3], (0, 255, 0), 2)
    return frame

def process_topdown(frame, src_points, log_func):
    dst_points = np.float32([[0, 0], [0, 600], [800, 0], [800, 600]])  # Updated for 800x600 resolution
    
    # Transformation matrix to change perspective
    transform_matrix = cv2.getPerspectiveTransform(np.float32(src_points), dst_points)
    return cv2.warpPerspective(frame, transform_matrix, (800, 600))

def process_topdown_imu(frame, imu_src_points, log_func):
    dst_points = np.float32([[0, 0], [0, 600], [800, 0], [800, 600]])  # Updated for 800x600 resolution

    # Transformation matrix to change perspective
    transform_matrix = cv2.getPerspectiveTransform(np.float32(imu_src_points), dst_points)
    return cv2.warpPerspective(frame, transform_matrix, (800, 600))