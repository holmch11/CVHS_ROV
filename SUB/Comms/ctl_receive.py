'''
ctl_receive.py

Receives Controller input from Control at 192.168.2.2:5800

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
2023/12/05 CEH Initial Version


####################################################################################
'''
import socket

def main():
    server_address = "192.168.2.2"  # Change this to the IP address of the server
    server_port = 5800  # Change this to the port used by the server

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_address, server_port))

    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            # Decode the received data and print it
            print(data.decode())
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()
