# Device Parameter Types Guide

This guide explains how to define different types of parameters for your SmartLab devices.

## Parameter Types Overview

SmartLab supports various parameter types to suit different use cases:

| Type | UI Control | Example Use Case |
|------|-----------|------------------|
| **Integer** | Number input | Data points, sample rate, duration |
| **Float** | Number input | Thresholds, gain values, calibration |
| **String** | Text input | Device IDs, file paths, comments |
| **String with options** | Dropdown/Select | Device types, modes, presets |
| **Boolean** | Checkbox | Enable/disable features |

## Basic Parameter Structure

All parameters share this basic structure:

```python
{
    "name": "parameterName",           # Internal identifier (no spaces)
    "displayName": "Parameter Name",   # User-facing name
    "type": "String",                  # Data type
    "defaultValue": "default",         # Default value
    "isRequired": True,                # Whether parameter is required
    "description": "Parameter description",  # Help text for users
    "unit": "ms"                       # Optional unit (for numbers)
}
```

## Choice Parameters (Dropdown/Select)

To create a parameter with predefined choices, add an `"options"` field:

```python
{
    "name": "deviceType",
    "displayName": "Device Type",
    "type": "String",
    "defaultValue": "Type A",
    "isRequired": True,
    "description": "Select the device type",
    "options": ["Type A", "Type B"]  # 👈 This creates a dropdown
}
```

### Example: Simple Two-Choice Parameter

```python
async def get_parameter_definitions(self) -> List[Dict]:
    return [
        {
            "name": "deviceType",
            "displayName": "Device Type",
            "type": "String",
            "defaultValue": "Type A",
            "isRequired": True,
            "description": "Select the device type",
            "options": ["Type A", "Type B"]
        }
    ]
```

In the UI, this will appear as a dropdown with two options: "Type A" and "Type B".

### Example: Multiple Choice Parameters

```python
async def get_parameter_definitions(self) -> List[Dict]:
    return [
        {
            "name": "deviceType",
            "displayName": "Device Type",
            "type": "String",
            "defaultValue": "Type A",
            "isRequired": True,
            "description": "Hardware variant",
            "options": ["Type A", "Type B"]
        },
        {
            "name": "measurementMode",
            "displayName": "Measurement Mode",
            "type": "String",
            "defaultValue": "Normal",
            "isRequired": True,
            "description": "Speed vs accuracy tradeoff",
            "options": ["Fast", "Normal", "Precise"]
        },
        {
            "name": "dataPoints",
            "displayName": "Number of Data Points",
            "type": "Integer",
            "defaultValue": 100,
            "isRequired": True,
            "unit": "points",
            "description": "Samples to collect"
            # No "options" = free number input
        }
    ]
```

## Using Choice Parameters in Your Code

### Reading Selected Values

```python
async def generate_measurement_data(self) -> List[Dict]:
    # Get the selected device type
    device_type = self.measurement_parameters.get("deviceType", "Type A")

    # Different behavior based on selection
    if device_type == "Type A":
        return await self._measure_type_a()
    elif device_type == "Type B":
        return await self._measure_type_b()
```

### Validating Choice Parameters

Always validate that the selected value is valid:

```python
def validate_parameters(self, parameters: Dict) -> Tuple[bool, str]:
    # Validate deviceType choice
    if "deviceType" in parameters:
        valid_types = ["Type A", "Type B"]
        if parameters["deviceType"] not in valid_types:
            return False, f"deviceType must be one of: {', '.join(valid_types)}"

    return True, ""
```

## Complete Example

Here's a complete device with choice parameters:

```python
from base_finite_device import BaseFiniteDevice
from typing import List, Dict, Tuple
import asyncio

class MyDevice(BaseFiniteDevice):
    def get_device_name(self) -> str:
        return "Multi-Mode Device"

    async def get_parameter_definitions(self) -> List[Dict]:
        return [
            {
                "name": "deviceType",
                "displayName": "Device Type",
                "type": "String",
                "defaultValue": "Type A",
                "isRequired": True,
                "description": "Select device hardware type",
                "options": ["Type A", "Type B"]
            },
            {
                "name": "mode",
                "displayName": "Measurement Mode",
                "type": "String",
                "defaultValue": "Normal",
                "isRequired": True,
                "description": "Measurement speed",
                "options": ["Fast", "Normal", "Precise"]
            },
            {
                "name": "samples",
                "displayName": "Sample Count",
                "type": "Integer",
                "defaultValue": 100,
                "isRequired": True,
                "unit": "samples",
                "description": "Number of samples"
            }
        ]

    async def generate_measurement_data(self) -> List[Dict]:
        device_type = self.measurement_parameters.get("deviceType", "Type A")
        mode = self.measurement_parameters.get("mode", "Normal")
        samples = self.measurement_parameters.get("samples", 100)

        # Configure based on selections
        if mode == "Fast":
            delay = 0.001
        elif mode == "Normal":
            delay = 0.01
        else:  # Precise
            delay = 0.1

        data = []
        for i in range(samples):
            await asyncio.sleep(delay)

            value = self._read_sensor(device_type)
            data.append({"value": value})

        return data

    def _read_sensor(self, device_type: str) -> float:
        # Device-specific reading logic
        if device_type == "Type A":
            return 25.0  # Simulate Type A reading
        else:
            return 50.0  # Simulate Type B reading

    def validate_parameters(self, parameters: Dict) -> Tuple[bool, str]:
        # Validate choices
        if "deviceType" in parameters:
            if parameters["deviceType"] not in ["Type A", "Type B"]:
                return False, "Invalid device type"

        if "mode" in parameters:
            if parameters["mode"] not in ["Fast", "Normal", "Precise"]:
                return False, "Invalid mode"

        # Validate samples
        samples = parameters.get("samples", 100)
        if not isinstance(samples, int) or samples < 1 or samples > 10000:
            return False, "Samples must be between 1 and 10000"

        return True, ""
```

## Testing Choice Parameters

### Test with Default Values
```bash
python test_device.py my_device.py
```

### Test with Type A
```bash
python test_device.py my_device.py --parameters '{"deviceType": "Type A"}'
```

### Test with Type B and Precise Mode
```bash
python test_device.py my_device.py --parameters '{"deviceType": "Type B", "mode": "Precise"}'
```

### Test with All Parameters
```bash
python test_device.py my_device.py --parameters '{"deviceType": "Type B", "mode": "Fast", "samples": 50}'
```

## Best Practices

### 1. Use Descriptive Option Names
```python
# Good: Clear and descriptive
"options": ["High Accuracy", "Low Power", "Balanced"]

# Avoid: Cryptic codes
"options": ["HA", "LP", "BAL"]
```

### 2. Provide Good Descriptions
```python
{
    "name": "mode",
    "displayName": "Measurement Mode",
    "description": "Fast: 10ms/sample, Normal: 50ms/sample, Precise: 100ms/sample",
    "options": ["Fast", "Normal", "Precise"]
}
```

### 3. Choose Sensible Defaults
```python
# Set the most commonly used option as default
"defaultValue": "Normal",  # Most users want this
"options": ["Fast", "Normal", "Precise"]
```

### 4. Always Validate
Even though the UI provides choices, always validate in `validate_parameters()`:

```python
def validate_parameters(self, parameters: Dict) -> Tuple[bool, str]:
    # User might bypass UI or use test script with wrong values
    if "deviceType" in parameters:
        valid_types = ["Type A", "Type B"]
        if parameters["deviceType"] not in valid_types:
            return False, f"deviceType must be one of: {', '.join(valid_types)}"
    return True, ""
```

## Common Use Cases

### Hardware Variants
```python
"options": ["Model X1", "Model X2", "Model X3"]
```

### Measurement Modes
```python
"options": ["Single Shot", "Continuous", "Triggered"]
```

### Quality/Speed Tradeoff
```python
"options": ["Fast", "Normal", "High Quality"]
```

### Communication Protocol
```python
"options": ["USB", "Serial", "Ethernet", "Bluetooth"]
```

### Sensor Type Selection
```python
"options": ["Temperature", "Humidity", "Pressure", "Combined"]
```

### Calibration Presets
```python
"options": ["Factory Default", "Custom 1", "Custom 2", "Lab Standard"]
```

## UI Rendering

In SmartLab's UI, parameters with `"options"` will render as:
- **Dropdown menu** (HTML `<select>`) on desktop
- **Radio buttons** for 2-3 options (optional, based on UI design)
- **Dropdown** for 4+ options

Parameters without `"options"` render as:
- **Number input** for Integer/Float types
- **Text input** for String type
- **Checkbox** for Boolean type

## See Also

- `example_device_with_choices.py` - Working example with choice parameters
- `DEVICE_TESTING_GUIDE.md` - How to test device implementations
- `base_finite_device.py` - Base class documentation
