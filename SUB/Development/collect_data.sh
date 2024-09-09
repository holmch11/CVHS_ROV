#!/bin/bash
#
# collect_data.sh
#
# Collect data from various python scripts controlling varios sensors and put in one place
#
# Version History
#**********************************************************************#
# 2023-12-05 CEH Initial Version Chris Holm holmch@oregonstate.edu
#
#
#**********************************************************************#
# Define data streams
#

webpage="192.168.2.3"
imu_data=$(python3 ~/CVHS_SUB/Comms/plot_imu_data.py)
extPressure=$(python3 ~/CVHS_SUB/Comms/sensors/ms5837-python/extPressure.py)
curl -X POST -d "output=${imu_data}" "${webpage}"

#source ~/CVHS_SUB/Comms/env/bin/activate
#python3 ~/CVHS_SUB/Comms/sensors/bme680.py
#deactivate

