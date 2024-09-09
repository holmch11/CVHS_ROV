'''
read_controller.py

Intakes Game Controller output and streams to ROV over port 5800

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
2023/12/01 CEH Initial Version


####################################################################################
'''
#!/usr/bin/python
import socket
import get_controller as getctl
from evdev import InputDevice, categorize, ecodes

path = getctl.path   
device = InputDevice(path)

def send_event(client_socket, event_type, event_code, event_value):
    message = f"{event_type} {event_code} {event_value}\n"
    client_socket.sendall(message.encode())
    
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("192.168.2.2",5800))  # Change the port as needed
    server_socket.listen()

    print("TCP server listening on port 5800")
    while True:
        client_socket, _ = server_socket.accept()
        
        # Process events from the Gamepad
        for event in device.read_loop():
            if event.type == ecodes.EV_KEY:
                # Handle button events
                key_event = categorize(event)
                send_event(client_socket, "BUTTON", key_event.keycode, key_event.keystate)
                
            elif event.type == ecodes.EV_ABS:
                # Handle axis events
                abs_event = categorize(event)
                send_event(client_socket, "AXIS", abs_event.event.code, abs_event.event.value)


if __name__ == "__main__":
    main()
