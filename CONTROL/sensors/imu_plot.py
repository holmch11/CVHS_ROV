'''
imu_plot.py

Receives imu input from sub at 192.168.2.3:5610

Copyright (c) 2023
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
2023/01/05 CEH Initial Version


####################################################################################
'''
#!/usr/bin/python
import socket
import struct
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
import signal
import sys

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 4), sharex=True)
plt.tight_layout()

time_data = []
Gx_data = []
Gy_data = []
Gz_data= []
Ax_data = []
Ay_data = []
Az_data = []

line_Gx, =ax1.plot(time_data, Gx_data, label='Gx')
line_Gy, =ax1.plot(time_data, Gy_data, label='Gy')
line_Gz, =ax1.plot(time_data, Gz_data, label='Gz')
line_Ax, =ax2.plot(time_data, Ax_data, label='Ax')
line_Ay, =ax2.plot(time_data, Ay_data, label='Ay')
line_Az, =ax2.plot(time_data, Az_data, label='Az')

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("192.168.2.3", 5610))  # Change the IP address and port as needed

ax1.legend()

def update_plot(frame):
    global time_data, Gx_data, Gy_data, Gz_data, Ax_data, Ay_data, Az_data  # Declare as global variables

    try:
        data = client_socket.recv(24)
        if not data:
            ani.event_source.stop()  # Stop the animation when the socket is closed
            plt.close(fig)  # Close the figure
            return line_Gx, line_Gy, line_Gz, line_Ax, line_Ay, line_Az

        Gx, Gy, Gz, Ax, Ay, Az = struct.unpack('ffffff', data)
        formatted_data = f"Gx: {Gx:.2f} deg/s Gy: {Gy:.2f} deg/s Gz: {Gz:.2f} deg/s\tAx: {Ax:.2f} g Ay: {Ay:.2f} g Az: {Az:.2f} g"
        print(f"IMU: {formatted_data}")

        time_data.append(time.time())
        Gx_data.append(Gx)
        Gy_data.append(Gy)
        Gz_data.append(Gz)
        Ax_data.append(Ax)
        Ay_data.append(Ay)
        Az_data.append(Az)

        # Limit the number of data points to display (adjust as needed)
        max_data_points = 100
        time_data = time_data[-max_data_points:]
        Gx_data = Gx_data[-max_data_points:]
        Gy_data = Gy_data[-max_data_points:]
        Gz_data = Gz_data[-max_data_points:]
        Ax_data = Ax_data[-max_data_points:]
        Ay_data = Ay_data[-max_data_points:]
        Az_data = Az_data[-max_data_points:]

        line_Gx.set_data(time_data, Gx_data)
        line_Gy.set_data(time_data, Gy_data)
        line_Gz.set_data(time_data, Gz_data)
        line_Ax.set_data(time_data, Ax_data)
        line_Ay.set_data(time_data, Ay_data)
        line_Az.set_data(time_data, Az_data)

        ax1.relim()
        ax1.autoscale_view()
        ax2.relim()
        ax2.autoscale_view()

        plt.suptitle('IMU Data')
        plt.xlabel('Time')
        ax1.set_ylabel('Degrees/sec')
        ax2.set_ylabel('g')

    except OSError as e:
        print(f"Error receiving data: {e}")

    return line_Gx, line_Gy, line_Gz, line_Ax, line_Ay, line_Az

def on_close(event):
    print("Graph closed. Exiting...")
    plt.ioff()
    client_socket.close()
    sys.exit(0)

# Connect the close_event of the figure to on_close function
fig.canvas.mpl_connect('close_event', on_close)

def main():
    print("Connected to IMU server on port 5610")

    try:
        plt.ion()
        ani = FuncAnimation(fig, update_plot, blit=False)
        plt.get_current_fig_manager().set_window_title('IMU Sensor')
        plt.show(block=True)  # Add block=True to make plt.show() block execution

        # Handle Ctrl+C gracefully
        def signal_handler(sig, frame):
            print("\nExiting...")
            plt.ioff()
            client_socket.close()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        while True:
            time.sleep(1)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        plt.ioff()
        client_socket.close()

if __name__ == "__main__":
    main()
