'''
SubControl.py

This creates the GUI interface for controlling the CVHS ROV, it replaces several scripts that could exist independently:
extPressure.py, imu_plot.py, intPressure.py, battery.py, activate.py and video.  read_controller.py and subsequenty setup-new-ctl.py is
automatically started by control.service. These exist outside of the GUI and should automatically restart as necessary.

Copyright (c) 2024
Created by Christopher Holm
holmch@oregonstate.edu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Revision History
#####################################################################################
2024/02/12 CEH Initial Version


####################################################################################
'''
import socket
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import struct
import time
import cv2
from PIL import Image, ImageTk
import numpy as np

class SensorGraphApp:
    def __init__(self, root, imu_socket, ext_pressure_socket, int_pressure_socket, video_socket, enable_socket, battery_socket):
        self.root = root
        self.root.title("Sensor Data Visualization")

        # Create Matplotlib figures for different graphs
        self.fig, self.ax_imu = plt.subplots(figsize=(8, 4))
        self.ax_imu.set_title("IMU Data")
        self.ax_imu.set_xlabel("Time (s)")
        self.ax_imu.set_ylabel("Angular Velocity (deg/s) / Acceleration (g)")

        self.ax_ext_pressure = self.fig.add_subplot(3, 2, 2)
        self.ax_ext_pressure.set_title("External Pressure")
        self.ax_ext_pressure.set_xlabel("Time (s)")
        self.ax_ext_pressure.set_ylabel("Pressure (Pa)")
        self.ax2_ext_pressure.set_ylabel("Depth (m)")

        self.ax_int_pressure = self.fig.add_subplot(3, 2, 4)
        self.ax_int_pressure.set_title("Internal Pressure")
        self.ax_int_pressure.set_xlabel("Time (s)")
        self.ax_int_pressure.set_ylabel("Pressure (Pa) / Humidty (%RH) ")
        self.ax2_int_pressure.set_ylabel("Battery Voltage (V)")
        # Create Tkinter canvas for Matplotlib
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Set up sockets
        self.imu_socket = imu_socket
        self.ext_pressure_socket = ext_pressure_socket
        self.int_pressure_socket = int_pressure_socket
        self.video_socket = video_socket
        self.enable_socket = enable_socket

        # Lists for storing data
        self.time_series = []
        self.imu_data = []
        self.ext_pressure_data = []
        self.int_pressure_data = []

        # Create OpenCV VideoCapture
        self.video_capture = cv2.VideoCapture()

        # Display video stream using OpenCV
        self.video_label = tk.Label(self.root)
        self.video_label.pack()

        # Create a button to send the "Activate" or "Deactivate" message
        self.active_button = tk.Button(self.root, text="Enable", command=self.toggle_button_state)
        self.active_button.pack(pady=20)

        # Update the graphs and video
        self.update_graphs()
        self.update_video()

    def update_graphs(self):
        # Update IMU data
        self.update_sensor_data(self.ax_imu, self.imu_socket, self.time_series, self.imu_data, 'IMU')

        # Update external pressure data
        self.update_sensor_data(self.ax_ext_pressure, self.ext_pressure_socket, self.time_series, self.ext_pressure_data, 'Ext Pressure')

        # Update internal pressure data
        self.update_sensor_data(self.ax_int_pressure, self.int_pressure_socket, self.time_series, self.int_pressure_data, 'Int Pressure')

        # Call this method periodically to update the graphs
        self.canvas.draw()
        self.root.after(1000, self.update_graphs)  # 1000 milliseconds (1 second) update interval

    def update_sensor_data(self, ax, sensor_socket, time_series, data, sensor_name):
        try:
            sensor_data = sensor_socket.recv(24)
            if not sensor_data:
                return

            sensor_values = struct.unpack('ffffff', sensor_data)
            current_time = time.time()

            # Process the data as needed
            time_series.append(current_time)
            data.append(sensor_values)

            # Update the plot
            ax.clear()
            ax.plot(time_series, data)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel(sensor_name)
            ax.set_title(f"{sensor_name} Data")

        except OSError as e:
            print(f"Error receiving {sensor_name} data: {e}")

    def update_video(self):
        try:
            # Receive video frame from the socket
            frame_data = self.video_socket.recv(921600)  # Adjust the buffer size based on your video frame size
            if not frame_data:
                return

            # Convert frame data to numpy array
            frame_np = np.frombuffer(frame_data, dtype=np.uint8).reshape(480, 640, 3)

            # Convert numpy array to Image
            frame_img = Image.fromarray(frame_np)

            # Convert Image to PhotoImage
            frame_tk = ImageTk.PhotoImage(image=frame_img)

            # Update the label with the new frame
            self.video_label.configure(image=frame_tk)
            self.video_label.image = frame_tk

        except Exception as e:
            print(f"Error receiving video data: {e}")

        # Call this method periodically to update the video stream
        self.root.after(33, self.update_video)  # 30 frames per second (33 milliseconds per frame)

    def toggle_button_state(self):
        current_state = self.active_button.cget("text")
        new_state = "Disable" if current_state == "Enable" else "Enable"
        self.active_button.config(text=new_state)

        # Send the corresponding message to the server on port 5640 (enable_socket)
        send_message(self.enable_socket, current_state.lower())

# Updated send_message function
def send_message(socket, message):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(("192.168.2.3", 5640))  # Change the IP address if needed
        client_socket.sendall(message.encode('utf-8'))
        client_socket.close()
        print(f"Sent '{message}' message to the server on port 5640")
    except Exception as e:
        print(f"Error sending message: {e}")

if __name__ == "__main__":
    root = tk.Tk()

    # Connect to the different sensor servers
    video_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    video_socket.connect(("192.168.2.3", 5600))

    imu_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    imu_socket.connect(("192.168.2.3", 5610))

    ext_pressure_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ext_pressure_socket.connect(("192.168.2.3", 5620))

    int_pressure_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    int_pressure_socket.connect(("192.168.2.3", 5630))

    enable_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    enable_socket.connect(("192.168.2.3", 5640))

    battery_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    enable_socket.connect(("192.168.2.3", 5650))

    app = SensorGraphApp(root, imu_socket, ext_pressure_socket, int_pressure_socket, video_socket, enable_socket, battery_socket)
    root.mainloop()

    # Close the sockets when the Tkinter application is closed
    video_socket.close()
    imu_socket.close()
    ext_pressure_socket.close()
    int_pressure_socket.close()
    enable_socket.close()
    battery_socket.close()
