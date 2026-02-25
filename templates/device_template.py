"""
Device Template for Creating New Finite Measurement Devices

This template provides a starting point for implementing new measurement devices
that communicate with the Smart Home app. Copy this file and customize the
abstract method implementations for your specific device.

Steps to create a new device:
1. Copy this file and rename it (e.g., temperature_sensor_device.py)
2. Rename the class (e.g., TemperatureSensorDevice)
3. Update get_device_name() to return your device's display name
4. Define your parameters in get_parameter_definitions()
5. Implement the measurement logic in generate_measurement_data()
6. Add parameter validation in validate_parameters()
7. Add any device-specific helper methods as needed
8. Test with the Smart Home app

Example usage:
    python your_device.py <device_id>
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Tuple

from src.base_finite_device import BaseFiniteDevice


class YourDeviceNameHere(BaseFiniteDevice):
    """
    [Provide a brief description of your device]

    This device measures [what it measures] using [hardware/protocol/method].

    Supported parameters:
    - [parameter1]: [description]
    - [parameter2]: [description]
    """

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

        # Add your device-specific attributes here
        # Examples:
        # self.serial_port = None
        # self.sensor_handle = None
        # self.calibration_data = {}
        # self.hardware_version = "1.0"

    # =========================================================================
    # Required Abstract Method Implementations
    # =========================================================================

    def get_device_name(self) -> str:
        """
        Return the display name of your device.

        This name will be shown to users in the Smart Home app interface.

        Returns:
            Human-readable device name

        Example:
            return "DS18B20 Temperature Sensor"
        """
        return "Your Device Name"  # TODO: Change this!

    async def get_parameter_definitions(self) -> List[Dict]:
        """
        Define what parameters your device needs for measurement.

        Each parameter is a dictionary with the following fields:
        - name (str): Internal parameter name (use camelCase)
        - displayName (str): User-facing name
        - type (str): Data type - "Integer", "Float", "String", "Boolean"
        - defaultValue: Default value matching the type
        - isRequired (bool): Whether this parameter is required
        - unit (str, optional): Unit of measurement (e.g., "Hz", "seconds", "V")
        - description (str): User-friendly explanation

        Returns:
            List of parameter definition dictionaries

        Example:
            return [
                {
                    "name": "sampleRate",
                    "displayName": "Sample Rate",
                    "type": "Integer",
                    "defaultValue": 100,
                    "isRequired": True,
                    "unit": "Hz",
                    "description": "Number of samples per second"
                },
                {
                    "name": "duration",
                    "displayName": "Measurement Duration",
                    "type": "Float",
                    "defaultValue": 10.0,
                    "isRequired": True,
                    "unit": "seconds",
                    "description": "How long to collect data"
                }
            ]
        """
        # TODO: Define your device's parameters
        return [
            {
                "name": "exampleParam",
                "displayName": "Example Parameter",
                "type": "Integer",
                "defaultValue": 10,
                "isRequired": True,
                "unit": "units",
                "description": "This is an example parameter - replace with your own"
            }
        ]

    async def generate_measurement_data(self) -> List[Dict]:
        """
        Implement your device's measurement logic.

        This method should:
        1. Read configuration from self.measurement_parameters
        2. Acquire data from your hardware/sensor/source
        3. Return a list of measurement data points

        Each data point should be a dictionary containing relevant measurement
        information. Common fields include:
        - timestamp: ISO format timestamp
        - value: Measured value
        - unit: Unit of measurement
        - [other fields as needed for your device]

        You can include progress logging to inform users about measurement status.

        Returns:
            List of measurement data point dictionaries

        Example:
            num_samples = self.measurement_parameters.get("numSamples", 10)
            sample_rate = self.measurement_parameters.get("sampleRate", 100)

            data = []
            for i in range(num_samples):
                # Read from your hardware
                value = self.read_sensor()

                data.append({
                    "timestamp": datetime.now().isoformat(),
                    "value": value,
                    "unit": "°C"
                })

                # Progress reporting (optional but recommended)
                if (i + 1) % 100 == 0:
                    print(f"Collected {i+1}/{num_samples} samples", flush=True)

                # Wait between samples based on sample rate
                await asyncio.sleep(1.0 / sample_rate)

            return data
        """
        # TODO: Implement your measurement logic
        print("Starting measurement...", flush=True)

        # Example: Get parameters
        num_points = self.measurement_parameters.get("exampleParam", 10)

        data = []
        for i in range(num_points):
            # TODO: Replace with actual hardware reading
            # Example: value = self.read_from_hardware()

            # Simulate measurement delay
            await asyncio.sleep(0.1)

            data_point = {
                "timestamp": datetime.now().isoformat(),
                "value": i * 1.5,  # TODO: Replace with actual measurement
                "unit": "units"    # TODO: Replace with actual unit
            }
            data.append(data_point)

            # Progress reporting
            if (i + 1) % 10 == 0:
                print(f"Measured {i+1}/{num_points} data points", flush=True)

        print(f"Measurement complete: {len(data)} points collected", flush=True)
        return data

    def validate_parameters(self, parameters: Dict) -> Tuple[bool, str]:
        """
        Validate that provided parameters are acceptable for your device.

        Check for:
        - Required parameters are present
        - Values are within valid ranges
        - Types are correct
        - Hardware limitations are respected
        - Parameter combinations make sense

        Args:
            parameters: Dictionary of parameter name -> value pairs

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if all validations pass, False otherwise
            - error_message: Human-readable error description (empty if valid)

        Example:
            # Check required parameters
            if "sampleRate" not in parameters:
                return False, "sampleRate is required"

            # Type validation
            if not isinstance(parameters["sampleRate"], int):
                return False, "sampleRate must be an integer"

            # Range validation
            if parameters["sampleRate"] < 1 or parameters["sampleRate"] > 10000:
                return False, "sampleRate must be between 1 and 10000 Hz"

            # Hardware constraints
            if parameters["duration"] * parameters["sampleRate"] > 1000000:
                return False, "Total samples would exceed hardware buffer (max 1M)"

            return True, ""
        """
        # TODO: Implement parameter validation for your device

        # Example validation
        if "exampleParam" in parameters:
            value = parameters["exampleParam"]

            # Type check
            if not isinstance(value, int):
                return False, "exampleParam must be an integer"

            # Range check
            if value < 1 or value > 1000:
                return False, "exampleParam must be between 1 and 1000"

        # All validations passed
        return True, ""

    # =========================================================================
    # Optional: Device-Specific Helper Methods
    # =========================================================================

    def connect_to_hardware(self):
        """
        Example helper method for hardware connection.

        Add any device-specific methods you need here.
        """
        # TODO: Implement hardware connection logic
        pass

    def disconnect_from_hardware(self):
        """Example helper method for hardware disconnection."""
        # TODO: Implement hardware disconnection logic
        pass

    def read_from_hardware(self):
        """Example helper method for reading from hardware."""
        # TODO: Implement hardware reading logic
        pass

    def calibrate(self):
        """Example helper method for device calibration."""
        # TODO: Implement calibration logic if needed
        pass


# =========================================================================
# Entry Point
# =========================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python device_template.py <device_id>", flush=True)
        sys.exit(1)

    device_id = sys.argv[1]
    print(f"Starting device with ID: {device_id}", flush=True)
    print(f"Process ID: {os.getpid()}", flush=True)

    # Create and run device instance
    device = YourDeviceNameHere(device_id)

    try:
        asyncio.run(device.run())
    except KeyboardInterrupt:
        print("Device stopped by user", flush=True)
    except Exception as e:
        print(f"Device error: {e}", flush=True)
        import traceback
        traceback.print_exc()
