import serial
import serial.tools.list_ports
import threading
import cv2
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import tkinter as tk
from video_controls import update_all_frames
from tkinter import ttk, scrolledtext

roll_zero, pitch_zero, yaw_zero = 0.0, 0.0, 0.0

# Global variables
ser = None
roll, pitch, yaw = 0.0, 0.0, 0.0
data_ready = False
capture = cv2.VideoCapture('samples\\sample1\\front_camera.mp4')
# Cube vertices and faces (6 faces of the cube)
vertices = np.array([[-1, -1, -1],
                     [1, -1, -1],
                     [1, 1, -1],
                     [-1, 1, -1],
                     [-1, -1, 1],
                     [1, -1, 1],
                     [1, 1, 1],
                     [-1, 1, 1]])

# Cube faces
faces = [[0, 1, 2, 3],  # Bottom face
         [4, 5, 6, 7],  # Top face
         [0, 1, 5, 4],  # Front face
         [2, 3, 7, 6],  # Back face
         [0, 3, 7, 4],  # Left face
         [1, 2, 6, 5]]  # Right face

# Face colors for the cube sides
face_colors = ['red', 'blue', 'green', 'cyan', 'orange', 'purple']

def rotation_matrix(roll, pitch, yaw):
    """Generates the rotation matrix from roll, pitch, yaw."""
    roll = np.radians(roll)
    pitch = np.radians(pitch)
    yaw = np.radians(yaw)

    Rx = np.array([[1, 0, 0],
                   [0, np.cos(roll), -np.sin(roll)],
                   [0, np.sin(roll), np.cos(roll)]])
    
    Ry = np.array([[np.cos(pitch), 0, np.sin(pitch)],
                   [0, 1, 0],
                   [-np.sin(pitch), 0, np.cos(pitch)]])
    
    Rz = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                   [np.sin(yaw), np.cos(yaw), 0],
                   [0, 0, 1]])

    return Rz @ Ry @ Rx


def draw_cube(ax, vertices, faces, face_colors):
    """Draw the cube with the given vertices, faces, and colors."""
    ax.cla()
    ax.set_xlim([-1, 1])
    ax.set_ylim([-1, 1])
    ax.set_zlim([-1, 1])
    ax.xaxis.set_pane_color((0.0, 0.0, 0.0, 1.0))  # Set the x-axis pane to black
    ax.yaxis.set_pane_color((0.0, 0.0, 0.0, 1.0))  # Set the y-axis pane to black
    ax.zaxis.set_pane_color((0.0, 0.0, 0.0, 1.0))  # Set the z-axis pane to black
    ax.set_facecolor('black')  # Set background color to black
    ax.set_box_aspect([1, 1, 1])  # Keep the aspect ratio of the cube correct

    # Turn off the axes
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    # Draw faces
    for i, face in enumerate(faces):
        square = [vertices[vert] for vert in face]
        ax.add_collection3d(Poly3DCollection([square], color=face_colors[i], linewidths=1, edgecolors='k', alpha=0.8))

def update_plot(frame, ax):
    """Update the cube's orientation based on new roll, pitch, yaw data."""
    global roll, pitch, yaw, data_ready


    if data_ready:
        R = rotation_matrix(roll, pitch, yaw)
        rotated_vertices = vertices @ R.T
        draw_cube(ax, rotated_vertices, faces, face_colors)
        data_ready = False
        # Log the IMU data
        log_message(f"Roll: {roll:.2f}, Pitch: {pitch:.2f}, Yaw: {yaw:.2f}")

def log_message(message):
    """Log message to the logger box."""
    logger_textbox.config(state=tk.NORMAL)
    logger_textbox.insert(tk.END, message + "\n")
    logger_textbox.config(state=tk.DISABLED)
    logger_textbox.see(tk.END)

def read_serial_data():
    """Thread function to read serial data in real-time."""
    global roll, pitch, yaw, data_ready

    while ser and ser.is_open:
        try:
            # Read and decode serial data
            data = ser.readline().decode('utf-8', errors='ignore').strip()
            if data:
                # Parse roll, pitch, yaw values
                values = list(filter(None, data.split('*')))
                if len(values) == 3:
                    roll = float(values[0])
                    pitch = float(values[1])
                    yaw = float(values[2])
                    data_ready = True
        except Exception as e:
            log_message(f"Serial error: {e}")

def connect_serial_port(port):
    """Connect to the selected serial port."""
    global ser
    try:
        ser = serial.Serial(port, 115200, timeout=1)
        serial_thread = threading.Thread(target=read_serial_data)
        serial_thread.daemon = True
        serial_thread.start()
        status_label.config(text=f"Connected to {port}")
        open_port_button.config(text="Close Port", command=close_serial_port)  # Change button to "Close Port"
    except Exception as e:
        status_label.config(text=f"Failed to connect: {e}")
        log_message(f"Failed to connect: {e}")

def close_serial_port():
    """Close the serial port connection."""
    global ser
    if ser and ser.is_open:
        ser.close()
        status_label.config(text="Status: Port closed")
        log_message("Port closed")
        open_port_button.config(text="Open Port", command=on_open_com_port)  # Change button back to "Open Port"

def list_com_ports():
    """List available COM ports for the dropdown menu."""
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Create the main window
root = tk.Tk()
root.title("IMU Visualizer")
root.geometry("1630x1470")

# Set Tkinter scaling for high DPI displays
root.tk.call('tk', 'scaling', 2.0)

# Dropdown to select COM port
com_ports = list_com_ports()
com_var = tk.StringVar(value="Select a COM Port")
com_dropdown = ttk.Combobox(root, textvariable=com_var, values=com_ports, font=("Arial", 14))
com_dropdown.place(x=50, y=10, width=200, height=30)

# Button to open the selected COM port
def on_open_com_port():
    selected_port = com_dropdown.get()
    connect_serial_port(selected_port)

def on_reset_imu():
    global roll_zero, pitch_zero, yaw_zero
    roll_zero = roll
    yaw_zero = yaw
    pitch_zero = pitch
    log_message(f"IMU Reset to Roll:{roll} Pitch:{pitch} Yaw:{yaw}")

def on_play_video():
    schedule_update()
    log_message("Video Started")

open_port_button = tk.Button(root, text="Open Port", command=on_open_com_port, font=("Arial", 10))
open_port_button.place(x=270, y=10, width=100, height=30)

# Status label
status_label = tk.Label(root, text="Status: Not connected", font=("Arial", 14))
status_label.place(x=400, y=10, width=300, height=30)

reset_imu_button = tk.Button(root, text="Reset IMU", command=on_reset_imu, font=("Arial", 10))
reset_imu_button.place(x=710, y=10, width=100, height=30)

play_video_button = tk.Button(root, text="Play Video", command=on_play_video, font=("Arial", 10))
play_video_button.place(x=820, y=10, width=100, height=30)

# Create the matplotlib figure and axis
fig = plt.figure(figsize=(8, 8), dpi=100)  # Adjust the dpi and size to scale the figure
fig.patch.set_facecolor('black')  # Set figure background color to black
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('black')

# Embed the matplotlib figure in the Tkinter canvas
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()

# Set the canvas widget background color to black
canvas_widget.config(bg='black')  # Ensure the Tkinter canvas is also black
canvas_widget.place(x=820, y=660, width=800, height=600)
# Add a rich text logger (scrollable)
logger_textbox = scrolledtext.ScrolledText(root, height=10, width=120, state=tk.DISABLED, font=("Arial", 12))
logger_textbox.place(x=10, y=1270, width=1610, height=200)

topdown_frame = ttk.Label(root)
topdown_frame.place(x=10, y=50, width=800, height=600)

original_frame = ttk.Label(root)
original_frame.place(x=820, y=50, width=800, height=600)

imu_topdown_frame = ttk.Label(root)
imu_topdown_frame.place(x=10, y=660, width=800, height=600)

def get_imu_points(default_points, ratio=1):

    top_left = list(default_points[0])
    bottom_left = list(default_points[1])
    top_right = list(default_points[2])
    bottom_right = list(default_points[3])

    roll_adjustment = (roll - roll_zero) * ratio
    pitch_adjustment = (pitch - pitch_zero) * ratio
    yaw_adjustment = (yaw - yaw_zero) * ratio
    
    top_left[0] -= roll_adjustment + yaw_adjustment
    top_right[0] += roll_adjustment + yaw_adjustment

    top_left[1] -= pitch_adjustment
    top_right[1] -= pitch_adjustment

    return [tuple(map(int, top_left)), tuple(map(int, bottom_left)), tuple(map(int, top_right)), tuple(map(int, bottom_right))]

def get_default_points():
    top_left = (250, 334)  # Adjusted to match new frame size
    bottom_left = (0, 500)
    top_right = (570, 334)
    bottom_right = (800, 500)
    return [top_left, bottom_left, top_right, bottom_right]

def schedule_update():
    if root.winfo_exists():
        src_points = get_default_points()
        imu_src_points = get_imu_points(src_points)
        output = update_all_frames(capture, original_frame, topdown_frame, imu_topdown_frame, src_points, imu_src_points, log_message)
        root.after(10, schedule_update)

# Animation function
ani = FuncAnimation(fig, update_plot, fargs=(ax,), interval=10, cache_frame_data=False)

# Start the Tkinter main loop
root.mainloop()
capture.release()