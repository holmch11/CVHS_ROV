'''
intPressure.py

Receives BME680 data input from sub at 192.168.2.3:5630

Copyright (c) 2023
Created by Christopher Holm
holmch@oregonstate.edu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
f
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Revision History
#####################################################################################
2023/01/10 CEH Initial Version


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

# Define global variables for data storage
time_data = []
T_data = []
P_data = []
H_data = []

# Create a figure and axes for plotting
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()  # Create a twin axis for pressure
line_T, = ax1.plot(time_data, T_data, label='Temperature (C)', color='tab:red')
line_P, = ax2.plot(time_data, P_data, label='Pressure (hPa)', color='tab:blue')
line_H, = ax1.plot(time_data, H_data, label='Humidity (% RH)', color='tab:green')

# Connect to TCP socket on the server (replace IP and port with actual values)
server_address = ("192.168.2.3", 5630)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server_address)

# Set legends for both axes
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')

def update_plot(frame):
    global time_data, T_data, P_data, H_data

    try:
        # Receive data from the server
        data = client_socket.recv(16)
        if not data:
            ani.event_source.stop()  # Stop the animation when the socket is closed
            plt.close(fig)  # Close the figure
            return line_T, line_P, line_H

        # Unpack received data
        intTemp, intPres, intHum = struct.unpack('fff', data)
        formatted_data = f"T: {intTemp:.1f} deg C P: {intPres:.1f} hPa H: {intHum:.2f} % RH"
        print(f"BME680: {formatted_data}")

        # Append data to lists
        time_data.append(time.time())
        T_data.append(intTemp)
        P_data.append(intPres)
        H_data.append(intHum)

        # Limit the number of data points to display
        max_data_points = 100
        time_data = time_data[-max_data_points:]
        T_data = T_data[-max_data_points:]
        P_data = P_data[-max_data_points:]
        H_data = H_data[-max_data_points:]

        # Update plot data
        line_T.set_data(time_data, T_data)
        line_P.set_data(time_data, P_data)
        line_H.set_data(time_data, H_data)

        # Adjust plot limits and labels
        ax1.relim()
        ax1.autoscale_view()
        ax2.relim()
        ax2.autoscale_view()

    except OSError as e:
        print(f"Error receiving data: {e}")

    return line_T, line_P, line_H

def on_close(event):
    print("Graph closed. Exiting...")
    plt.ioff()
    client_socket.close()
    sys.exit(0)

# Connect the close_event of the figure to on_close function
fig.canvas.mpl_connect('close_event', on_close)

def main():
    print("Connected to Internal Pressure, Temperature, and Humidity server on port 5630")

    try:
        plt.ion()
        ani = FuncAnimation(fig, update_plot, interval=1000, blit=False)
        plt.get_current_fig_manager().set_window_title('Internal Pressure, Temperature, and Humidity Sensor')
        plt.show(block=True)

        # Handle Ctrl+C gracefully
        def signal_handler(sig, frame):
            print("\nExiting...")
            plt.ioff()
            client_socket.close()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        while True:
            time.sleep(0.5)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        plt.ioff()
        client_socket.close()

if __name__ == "__main__":
    main()