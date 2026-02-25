"""
Dummy finite measurement device implementation.

This device generates simulated measurement data for testing purposes.
It demonstrates how to implement a concrete device by inheriting from
BaseFiniteDevice and implementing the required abstract methods.
"""

import asyncio
import sys
import time
import os
from datetime import datetime
from typing import List, Dict, Tuple

from src.base_finite_device import BaseFiniteDevice


class DummyFiniteDevice(BaseFiniteDevice):
    """
    Dummy device implementation for testing and demonstration.

    Generates simulated measurement data with configurable data points
    and measurement types (temperature, humidity, pressure, etc.).
    """

    # =========================================================================
    # Abstract Method Implementations
    # =========================================================================

    def get_device_name(self) -> str:
        """Return the display name of this dummy device."""
        return "Dummy Finite Device"

    async def get_parameter_definitions(self) -> List[Dict]:
        """Return parameter definitions for dummy device."""
        return [
            {
                "name": "dataPoints",
                "displayName": "Number of Data Points",
                "type": "Integer",
                "defaultValue": 10,
                "isRequired": True,
                "unit": "points",
                "description": "Number of measurement points to collect"
            },
            {
                "name": "Option test",
                "displayName": "Trying out parameter options",
                "type": "String",
                "defaultValue": "Option A",
                "isRequired": True,
                "description": "Select options.",
                "options": ["Option A", "Option B"]                  
            }
            
        ]

    async def generate_measurement_data(self) -> List[Dict]:
        """Generate simulated measurement data based on parameters."""
        data_points = []

        # Get parameters
        num_points = self.measurement_parameters.get("dataPoints", 10)
        #measurement_type = self.measurement_parameters.get("measurementType", "temperature")

        #print(f"Generating {num_points} data points of type {measurement_type}...", flush=True)

        for i in range(num_points):
            # Simulate measurement process
            await asyncio.sleep(0.01)  # Simulate measurement time

            # Generate simulated value based on type
            value = 20.0 + (i * 0.5) + (time.time() % 10)  # Simulated temperature
            #if measurement_type == "temperature":
                
            
            data_points.append({
                "value": round(value, 2),
            })

            if (i + 1) % 10 == 0:
                print(f"Generated {i+1}/{num_points} data points", flush=True)

        print(f"Data generation complete: {len(data_points)} points", flush=True)
        return data_points

    def validate_parameters(self, parameters: Dict) -> Tuple[bool, str]:
        """Validate measurement parameters for dummy device."""
        # Check required parameter
        if "dataPoints" not in parameters: # maybe unnecessary
            return False, "dataPoints parameter is required"

        # Validate dataPoints type and range
        data_points = parameters.get("dataPoints")
        if not isinstance(data_points, int):
            return False, "dataPoints must be an integer"

        if data_points < 1:
            return False, "dataPoints must be at least 1"

        if data_points > 10000:
            return False, "dataPoints must not exceed 10000"

        # Validate measurement type if provided
        if "measurementType" in parameters:
            valid_types = ["temperature", "humidity", "pressure", "voltage", "current"]
            if parameters["measurementType"] not in valid_types:
                return False, f"measurementType must be one of: {', '.join(valid_types)}"

        return True, ""

    # =========================================================================
    # Helper Methods
    # =========================================================================

    

# =========================================================================
# Entry Point
# =========================================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python dummy_finite_measurement.py <device_id>", flush=True)
        sys.exit(1)

    device_id = sys.argv[1]
    print(f"Starting dummy device with ID: {device_id}", flush=True)
    print(f"Process ID: {os.getpid()}", flush=True)

    # Create and run device instance
    device = DummyFiniteDevice(device_id)

    try:
        asyncio.run(device.run())
    except KeyboardInterrupt:
        print("Device stopped by user", flush=True)
    except Exception as e:
        print(f"Device error: {e}", flush=True)
        import traceback
        traceback.print_exc()
