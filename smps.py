#!/usr/bin/env python

import serial
import time
from pymodbus.client.serial import ModbusSerialClient
import asyncio
import sys
import time
import os
from datetime import datetime
from typing import List, Dict, Tuple

from base_finite_device import BaseFiniteDevice

class SMPS(BaseFiniteDevice):
    """
    SMPS implementation for SmartLab app.
    """
    s

    def __init__(self, device_id: str):
        """
        Initialize your device.

        You can add device-specific initialization here, such as:
        - Hardware connections
        - Serial port setup
        - Configuration loading
        - Calibration data
        """
        # Always call parent constructor first
        super().__init__(device_id)
        self.serial_port = self.setup_serial_port()
        self.minvoltage_parameter_string = "minvoltage"
        self.maxvoltage_parameter_string = "maxvoltage"
        self.upscantime_parameter_string = "upscan"
        self.downscantime_parameter_string = "downscan"

    # =========================================================================
    # Subclass Method Implementations
    # =========================================================================
    
    
    def setup_serial_port(self):
        ser = serial.Serial(
            port='/dev/ttyUSB0',       # Change if needed
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=10  # in seconds

        )
        return ser



    # =========================================================================
    # Abstract Method Implementations
    # =========================================================================

    def get_device_name(self) -> str:
        """Return the display name of this dummy device. Initialization logic"""
        print(f"SMPS.get_device_name: Trying to open serial port")
        self.serial_port.open()
        if(not self.serial_port.is_open):
            print(f"SMPS.get_device_name: Serial port is not open on {self.serial_port.portstr}")
            return ""
        
        self.serial_port.write(b'RSN\r')

        # Read response
        response = self.serial_port.read(100)  # Read up to 100 bytes
        print("Device ID:", response.decode(errors='ignore').strip())

        self.serial_port.close()

    
        return f"SMPS (Serial number: {response.decode(errors='ignore').strip()})"

    async def get_parameter_definitions(self) -> List[Dict]:
        """Return parameter definitions for dummy device."""
        return [
            {
                "name": f"{self.minvoltage_parameter_string}",
                "displayName": "minimal voltage to set at DMA",
                "type": "Integer",
                "defaultValue": 10,
                "isRequired": True,
                "unit": "points",
                "description": "Minimum voltage set at DMA"
            },
            {
                "name": f"{self.maxvoltage_parameter_string}",
                "displayName": "maximal voltage to set at DMA",
                "type": "String",
                "defaultValue": "temperature",
                "isRequired": True,
                "description": "Type of measurement (temperature, humidity, pressure)"
            },  
            {
                "name": f"{self.upscantime_parameter_string}",
                "displayName": "upscan time for measurement",
                "type": "Integer",
                "defaultValue": 120,
                "isRequired": True,
                "description": "Upscan time for measurement"
            },
            {
                "name": f"{self.downscantime_parameter_string}",
                "displayName": "downscan time for measurement",
                "type": "Integer",
                "defaultValue": 15,
                "isRequired": True,
                "description": "downscan time for measurement"
            }
            
        ]

    async def generate_measurement_data(self) -> List[Dict]:
        """Generate simulated measurement data based on parameters."""
        data_points = []

        # Get parameters
        self.serial_port.write(f'ZB\r'.encode('utf-8'))
        response = self.serial_port.read(100) 
        if(not response.find("OK")):
            print("Received ERROR after trying to start SMPS scan.")

        foundDelimiterString = False
        while(foundDelimiterString):

            response = self.serial_port.read(100) 
            data_points.append(response)
            if(response.find("-")): foundDelimiterString = True

        return data_points

    def validate_parameters(self, parameters: Dict) -> Tuple[bool, str]:
        """Validate measurement parameters for dummy device."""
        #Send parameters to device and check response; validation made by device itself
        #Put every step in function that returns the response
        

        self.minvoltage = parameters.get(self.minvoltage_parameter_string)
        self.maxvoltage = parameters.get(self.maxvoltage_parameter_string)
        self.upscantime = parameters.get(self.maxvoltage_parameter_string)
        self.downscantime = parameters.get(self.maxvoltage_parameter_string)
        
        print(f"Setting voltage from min. voltage {self.minvoltage} V to {self.maxvoltage}...")
        self.serial_port.write(f'ZV{self.minvoltage},{self.maxvoltage}\r'.encode('utf-8'))
        response = self.serial_port.read(100) 
        print(f"Response: {response}")
        if(not response.find("OK")): return (False, "Received ERROR after setting voltages.")
        
        print(f"Setting upscan time to {self.upscantime/10} s and down scan time to {self.downscantime/10} s ...")
        self.serial_port.write(f'ZT0,{self.upscantime},{self.downscantime}\r'.encode('utf-8'))
        response = self.serial_port.read(100)
        print(f"Response: {response}")
        if(not response.find("OK")): return (False, "Received ERROR after setting upscan and downscan times.")

        print(f"Setting scan direction to up...")
        self.serial_port.write(b'ZU\r')
        response = self.serial_port.read(100)
        print(f"Response: {response}")
        if(not response.find("OK")): return(False, "Received ERROR after setting scan direction.")

        return(True,"Parameters OK")


    # =========================================================================
    # Helper Methods
    # =========================================================================




# =========================================================================
# Entry Point
# =========================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python smps.py <device_id>", flush=True)
        sys.exit(1)

    device_id = sys.argv[1]
    print(f"Starting SMPS with ID: {device_id}", flush=True)
    print(f"Process ID: {os.getpid()}", flush=True)

    # Create and run device instance
    device = SMPS(device_id)

    try:
        asyncio.run(device.run())
    except KeyboardInterrupt:
        print("Device stopped by user", flush=True)
    except Exception as e:
        print(f"Device error: {e}", flush=True)
        import traceback
        traceback.print_exc()
    








