'''
extPressure.py

Receives MS5837 data input from sub at 192.168.2.3:5620

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
import subprocess

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True)

time_data = []
TC_data = []
P_psi_data = []
D_m_data = []

line_TC, = ax1.plot(time_data, TC_data, label='Temperature (C)')
line_P_psi, = ax1.plot(time_data, P_psi_data, label='Pressure (psi)')
line_D_m, = ax2.plot(time_data, D_m_data, label='Depth (m)')

# Connect to TCP socket on server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("192.168.2.3", 5620))  # Change the IP address and port as needed

ax1.legend()

def update_plot(frame):
    global time_data, TC_data, P_psi_data, D_m_data  # Declare as global variables

    try:
        data = client_socket.recv(20)
        if not data:
            ani.event_source.stop()  # Stop the animation when the socket is closed
            plt.close(fig)  # Close the figure
            return line_TC, line_P_psi, line_D_m

        D_m, P_mbar, P_psi, TC, TF = struct.unpack('fffff', data)
        formatted_data = f"D: {D_m:.1f} m P: {P_mbar:.1f} mbar  {P_psi:.3f} psi\tT: {TC:.2f} C  {TF:.2f} F"
        print(f"MS5867: {formatted_data}")

        time_data.append(time.time())
        TC_data.append(TC)
        P_psi_data.append(P_psi)
        D_m_data.append(D_m)

        # Limit the number of data points to display (adjust as needed)
        max_data_points = 100
        time_data = time_data[-max_data_points:]
        TC_data = TC_data[-max_data_points:]
        P_psi_data = P_psi_data[-max_data_points:]
        D_m_data = D_m_data[-max_data_points:]

        line_TC.set_data(time_data, TC_data)
        line_P_psi.set_data(time_data, P_psi_data)
        line_D_m.set_data(time_data, D_m_data)

        ax1.relim()
        ax1.autoscale_view()
        ax2.relim()
        ax2.autoscale_view()

        plt.suptitle('External Pressure and Depth')
        plt.xlabel('Time')
        ax1.set_ylabel('Temperature (C) / Pressure (psi)')
        ax2.set_ylabel('Depth (m)')

    except OSError as e:
        print(f"Error receiving data: {e}")

    return line_TC, line_P_psi, line_D_m

def on_close(event):
    print("Graph closed. Exiting...")
    plt.ioff()
    client_socket.close()
    sys.exit(0)

# Connect the close_event of the figure to on_close function
fig.canvas.mpl_connect('close_event', on_close)

def main():
    print("Connected to External Depth/Pressure and Temperature server on port 5620")

    try:
        plt.ion()
        ani = FuncAnimation(fig, update_plot, blit=False)
        plt.get_current_fig_manager().set_window_title('External Pressure and Temperature Sensor')
        plt.show(block=True)  # Add block=True to make plt.show() block execution

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
 
 # After main loop ends, move the window to a specific position
    subprocess.run(["wmctrl", "-r", "External Pressure and Temperature Sensor", "-e", "0,100,100,-1,-1"])
