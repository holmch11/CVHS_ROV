'''
intHealth_send.py

Intakes BME680 output and streams to control over port 5630

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
2024/01/05 CEH Initial Version
2024/01/30 CEH Commented out seperate serial intake of Battery, this is now handled by control arduino...

####################################################################################
'''
#!/usr/bin/python
import time
import socket
import struct
import board
import adafruit_bme680
#import serial

#Define Battery Monitor Serial Port
#ser = serial.Serial('dev/ttyACM1', 9600) #will have to change to 115200 if implemented on uno...

# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)

# change this to match the location's pressure (hPa) at sea level
bme680.sea_level_pressure = 1012

# You will usually have to add an offset to account for the temperature of
# the sensor. This is usually around 5 degrees but varies by use. Use a
# separate temperature sensor to calibrate this one.
temperature_offset = -5
# Spew readings
def main():
	# Open TCP socket on SUB
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(("192.168.2.3", 5630))  # Change the port as needed
	server_socket.listen()
	print("Reading Internal Pressure, Humidity, and Temperature sending on port 5630")

	try:
		while True:
			client_socket, _ = server_socket.accept()
			while True:
				
				intTemp = bme680.temperature + temperature_offset
				intPres = bme680.pressure
				intHum = bme680.relative_humidity
				int_data = struct.pack('fff', intTemp, intPres, intHum)
				client_socket.sendall(int_data)
				time.sleep(0.25)
		client_socket.close()
		ser.close()
	except Exception as e:
		print(f"Error: {e}")
	finally:
		server_socket.close()

if __name__ == "__main__":
	main()
