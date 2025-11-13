"""
Example device with choice-based parameters.

This demonstrates how to create parameters with predefined options
that users can select from (like a dropdown menu in the UI).
"""

import asyncio
import sys
import os
from datetime import datetime
from typing import List, Dict, Tuple
from base_finite_device import BaseFiniteDevice


class ExampleChoiceDevice(BaseFiniteDevice):
    """
    Example device showing how to implement choice-based parameters.
    """

    def get_device_name(self) -> str:
        """Return the display name of this device."""
        return "Example Device with Choices"

    async def get_parameter_definitions(self) -> List[Dict]:
        """
        Return parameter definitions including choice-based parameters.

        For choice parameters, add an "options" field with a list of valid choices.
        """
        return [
            {
                "name": "deviceType",
                "displayName": "Device Type",
                "type": "String",
                "defaultValue": "Type A",
                "isRequired": True,
                "description": "Select the device type",
                "options": ["Type A", "Type B"]  # This makes it a choice parameter
            },
            {
                "name": "measurementMode",
                "displayName": "Measurement Mode",
                "type": "String",
                "defaultValue": "Fast",
                "isRequired": True,
                "description": "Measurement speed vs accuracy tradeoff",
                "options": ["Fast", "Normal", "Precise"]  # Multiple choice example
            },
            {
                "name": "dataPoints",
                "displayName": "Number of Data Points",
                "type": "Integer",
                "defaultValue": 10,
                "isRequired": True,
                "unit": "points",
                "description": "Number of measurement points to collect"
                # No "options" field = free text/number input
            }
        ]

    async def generate_measurement_data(self) -> List[Dict]:
        """Generate measurement data based on selected parameters."""
        data_points = []

        # Get parameters
        device_type = self.measurement_parameters.get("deviceType", "Type A")
        measurement_mode = self.measurement_parameters.get("measurementMode", "Normal")
        num_points = self.measurement_parameters.get("dataPoints", 10)

        print(f"Generating data for {device_type} in {measurement_mode} mode...", flush=True)

        # Different behavior based on device type
        if device_type == "Type A":
            base_value = 25.0
            variation = 2.0
        else:  # Type B
            base_value = 50.0
            variation = 5.0

        # Different measurement speed based on mode
        if measurement_mode == "Fast":
            delay = 0.01
            precision = 1
        elif measurement_mode == "Normal":
            delay = 0.05
            precision = 2
        else:  # Precise
            delay = 0.1
            precision = 3

        for i in range(num_points):
            await asyncio.sleep(delay)

            # Generate value with device-type-specific base and variation
            import random
            value = base_value + random.uniform(-variation, variation) + (i * 0.1)

            data_points.append({
                "value": round(value, precision),
                "unit": "°C" if device_type == "Type A" else "°F",
                "deviceType": device_type,
                "mode": measurement_mode
            })

            if (i + 1) % 10 == 0:
                print(f"Generated {i+1}/{num_points} data points", flush=True)

        print(f"Data generation complete: {len(data_points)} points", flush=True)
        return data_points

    def validate_parameters(self, parameters: Dict) -> Tuple[bool, str]:
        """Validate measurement parameters."""
        # Check required parameter
        if "dataPoints" not in parameters:
            return False, "dataPoints parameter is required"

        # Validate dataPoints
        data_points = parameters.get("dataPoints")
        if not isinstance(data_points, int):
            return False, "dataPoints must be an integer"
        if data_points < 1 or data_points > 10000:
            return False, "dataPoints must be between 1 and 10000"

        # Validate deviceType choice
        if "deviceType" in parameters:
            valid_types = ["Type A", "Type B"]
            if parameters["deviceType"] not in valid_types:
                return False, f"deviceType must be one of: {', '.join(valid_types)}"

        # Validate measurementMode choice
        if "measurementMode" in parameters:
            valid_modes = ["Fast", "Normal", "Precise"]
            if parameters["measurementMode"] not in valid_modes:
                return False, f"measurementMode must be one of: {', '.join(valid_modes)}"

        return True, ""


# =========================================================================
# Entry Point
# =========================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python example_device_with_choices.py <device_id>", flush=True)
        sys.exit(1)

    device_id = sys.argv[1]
    print(f"Starting example device with ID: {device_id}", flush=True)
    print(f"Process ID: {os.getpid()}", flush=True)

    device = ExampleChoiceDevice(device_id)

    try:
        asyncio.run(device.run())
    except KeyboardInterrupt:
        print("Device stopped by user", flush=True)
    except Exception as e:
        print(f"Device error: {e}", flush=True)
        import traceback
        traceback.print_exc()
