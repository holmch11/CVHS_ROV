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
2024/03/07 CEH Adding in Battery Display
####################################################################################
'''
import tkinter as tk
import socket
import threading

# Server configuration
server_ip = "192.168.2.3"
server_port_tcp = 5640
server_port_udp = 5650

def send_message(message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((server_ip, server_port_tcp))
            client_socket.sendall(message.encode('utf-8'))
            print(f"Sent '{message}' message to the server")
    except Exception as e:
        print(f"Error sending message: {e}")

def toggle_button_state():
    current_state = active_button.cget("text")
    new_state = "Disable" if current_state == "Enable" else "Enable"
    active_button.config(text=new_state)

    # Send the corresponding message to the server
    send_message(current_state.lower())

    # Disable the button for 5 seconds using a separate thread
    threading.Thread(target=disable_button_for_5_seconds).start()

def disable_button_for_5_seconds():
    active_button.config(state=tk.DISABLED)
    window.after(5000, enable_button)

def enable_button():
    active_button.config(state=tk.NORMAL)

def receive_battery_voltage():
    while True:
        data, addr = udp_socket.recvfrom(1024)
        voltage_message = data.decode('utf-8')
        print(f"Received battery voltage: {voltage_message}")

# Create the main window
window = tk.Tk()
window.title("Raspberry Pi Controller")

# Create a button to send the "Enable" or "Disable" message
active_button = tk.Button(window, text="Enable", command=toggle_button_state)
active_button.pack(pady=20)

# Set up UDP socket for receiving battery voltage updates
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(("0.0.0.0", server_port_udp))

# Start a thread to listen for battery voltage updates
battery_thread = threading.Thread(target=receive_battery_voltage, daemon=True)
battery_thread.start()

# Run the Tkinter main loop
window.mainloop()
