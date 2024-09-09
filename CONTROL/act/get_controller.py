'''
get_controller.py

Finds path for Game Controller

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
from evdev import InputDevice, list_devices

def find_device_path(device_name, devices):
    for device_path in devices:
        device = InputDevice(device_path)
        if device.name == device_name:
            return device_path
    return None

def devicePath():
    # Get a list of input devices
    devices = list_devices()
    Devices = [InputDevice(path) for path in list_devices()]
    
    # Specify the device name you are looking for
    target_device_name = "Logitech Gamepad F310"
    
    # Find the device path for the specified device name
    device_path = find_device_path(target_device_name, devices)

    if device_path:
        print(device_path)
        return device_path
        # now you can utilize the path
        
    else:
        print(f"Device '{target_device_name}' not found in the list of devices.")
        # Specify the device name you are looking for
        target_device_name = input("Enter the Controller device name: ")

        # Find the device path for the specified device name
        device_path = find_device_path(target_device_name, devices)
        
        if device_path:
            print(device_path)
            return device_path
            # Now you can use the device_path as needed
            
        else:
            print(f"Error Device '{target_device_name}' not found in the list of devices. Check This list and Try again")
            for device in Devices:
                print(device.name)
            return(OSError)

path = str(devicePath())
