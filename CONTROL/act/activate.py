'''
activate.py

Sends active to sub at 192.168.2.3:5640

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
2024/02/29 CEH Altered to intake Battery Voltage, handle restart better
2024/03/11 CEH Rolled Back version
####################################################################################
'''
import tkinter as tk
import socket
import threading
import subprocess

# Server configuration
server_ip = "192.168.2.3"
client_ip = "192.168.2.2"
server_port_tcp = 5640
server_port_udp = 5650
command_enable = ['sudo', 'systemctl', 'restart', 'control.service']
command_disable = ['sudo', 'systemctl', 'restart', 'control.service']

def send_message(message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_ip, server_port_tcp))
            client_socket.sendall(message.encode('utf-8'))
            print(f"Sent '{message}' message to the server")
    except Exception as e:
        print(f"Error sending message: {e}")

def toggle_button_state():
    current_state = active_button.cget("text").lower()  # Get the lowercase text

    if current_state == "enable":
        # If currently enabled, send "enable"
        send_message("enable")
    else:
        # If currently disabled, send "disable" and restart control.service
        send_message("disable")
        subprocess.run(command_disable, check=True)
        print("The control.service has been restarted successfully.")

    # Update the button state and disable it for 5 seconds
    new_state = "Disable" if current_state == "enable" else "Enable"
    active_button.config(text=new_state)
    active_button.config(state=tk.DISABLED)
    window.after(5000, enable_button)

def enable_button():
    active_button.config(state=tk.NORMAL)

# Create the main window
window = tk.Tk()
window.title("Raspberry Pi Controller")

# Create a button to send the "Enable" or "Disable" message
active_button = tk.Button(window, text="Enable", command=toggle_button_state)
active_button.pack(pady=20)

# Create a label to display battery voltage
voltage_label = tk.Label(window, text="Battery Voltage: N/A")
voltage_label.pack(pady=10)

# Set up UDP socket for receiving battery voltage updates
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind((client_ip, server_port_udp))

# Start a thread to listen for battery voltage updates
def receive_battery_voltage():
    while True:
        data, addr = udp_socket.recvfrom(1024)
        print(f"Received raw data: {data}")

        try:
            # Attempt to decode the data as a string
            voltage_message = data.decode('utf-8')

            # If successful, update the label with the received battery voltage
            print(f"Decoded battery voltage: {voltage_message}")
            voltage_label.config(text=f"Battery Voltage: {voltage_message}")

        except UnicodeDecodeError as e:
            print(f"Error decoding data: {e}")

        except Exception as e:
            print(f"Unexpected error: {e}")

battery_thread = threading.Thread(target=receive_battery_voltage, daemon=True)
battery_thread.start()

# Run the Tkinter main loop
window.mainloop()
