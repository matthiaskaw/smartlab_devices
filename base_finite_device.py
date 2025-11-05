"""
Base class for finite measurement devices.

This module provides the abstract base class for all finite measurement devices
that communicate with the Smart Home app via named pipes (Windows) or UNIX
domain sockets (Linux).

The base class handles:
- Platform-specific IPC communication
- Command protocol parsing and routing
- Connection lifecycle management
- Response formatting and sending

Device implementations only need to implement the abstract methods for:
- Device identification
- Parameter definitions
- Measurement data generation
- Parameter validation
"""

import asyncio
import json
import sys
import time
import os
import platform
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Tuple, Optional

# Platform-specific imports
IS_WINDOWS = platform.system() == "Windows"
IS_LINUX = platform.system() == "Linux"

if IS_WINDOWS:
    import win32pipe
    import win32file
    import pywintypes
elif IS_LINUX:
    import socket
    import struct
else:
    raise RuntimeError(f"Unsupported platform: {platform.system()}")


class BaseFiniteDevice(ABC):
    """
    Abstract base class for finite measurement devices.

    This class provides all the infrastructure for IPC communication and
    command handling. Subclasses must implement the abstract methods to
    define device-specific behavior.

    Attributes:
        device_id (str): Unique identifier for this device instance
        should_stop (bool): Flag to signal shutdown
        measurement_parameters (dict): Current measurement configuration
    """

    def __init__(self, device_id: str):
        """
        Initialize the base device.

        Args:
            device_id: Unique identifier for this device instance
        """
        self.device_id = device_id
        self.should_stop = False
        self.measurement_parameters = {}

        # Platform-specific pipe paths and handles
        if IS_WINDOWS:
            self.server_to_client_pipe = f"\\\\.\\pipe\\serverToClient_{device_id}"
            self.client_to_server_pipe = f"\\\\.\\pipe\\clientToServer_{device_id}"
            self.pipe_read_handle = None
            self.pipe_write_handle = None
        elif IS_LINUX:
            self.server_to_client_pipe = f"/tmp/CoreFxPipe_serverToClient_{device_id}"
            self.client_to_server_pipe = f"/tmp/CoreFxPipe_clientToServer_{device_id}"
            self.read_socket = None
            self.write_socket = None

        print(f"Platform: {platform.system()}", flush=True)

    # =========================================================================
    # Abstract Methods - Must be implemented by subclasses
    # =========================================================================

    @abstractmethod
    def get_device_name(self) -> str:
        """
        Return the display name of this device. 

        This name will be shown to users in the Smart Home app.NO!!!

        Returns:
            Human-readable device name (e.g., "Temperature Sensor", "Dummy Device")
        """
        pass

    @abstractmethod
    async def get_parameter_definitions(self) -> List[Dict]:
        """
        Return the list of parameters this device accepts.

        Each parameter definition should be a dictionary with:
        - name (str): Internal parameter name
        - displayName (str): User-facing parameter name
        - type (str): Parameter type (Integer, Float, String, Boolean)
        - defaultValue: Default value for the parameter
        - isRequired (bool): Whether this parameter is required
        - unit (str, optional): Unit of measurement
        - description (str): Human-readable description

        Returns:
            List of parameter definition dictionaries

        Example:
            [
                {
                    "name": "sampleRate",
                    "displayName": "Sample Rate",
                    "type": "Integer",
                    "defaultValue": 100,
                    "isRequired": True,
                    "unit": "Hz",
                    "description": "Sampling frequency"
                }
            ]
        """
        pass

    @abstractmethod
    async def generate_measurement_data(self) -> List[Dict]:
        """
        Generate or acquire measurement data.

        This method should read from hardware, simulate data, or otherwise
        produce measurement data points based on self.measurement_parameters.

        Returns:
            List of measurement data point dictionaries. Each should contain
            relevant measurement information (format is device-specific, but
            typically includes timestamp, value, and unit).

        Example:
            [
                {
                    "timestamp": "2025-01-15T10:30:00.123456",
                    "value": 23.5,
                    "unit": "°C"
                },
                ...
            ]
        """
        pass

    @abstractmethod
    def validate_parameters(self, parameters: Dict) -> Tuple[bool, str]:
        """
        Validate measurement parameters before accepting them.

        Check that:
        - Required parameters are present
        - Values are within valid ranges
        - Types are correct
        - Hardware constraints are satisfied

        Args:
            parameters: Dictionary of parameter name -> value pairs

        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if parameters are valid, False otherwise
            - error_message: Human-readable error message (empty if valid)

        Example:
            if "sampleRate" not in parameters:
                return False, "sampleRate is required"
            if parameters["sampleRate"] > 1000:
                return False, "sampleRate must be <= 1000 Hz"
            return True, ""
        """
        pass

    # =========================================================================
    # Main Execution Loop
    # =========================================================================

    async def run(self):
        """
        Main execution loop for the device.

        This method:
        1. Connects to IPC pipes
        2. Starts listening for commands
        3. Handles cleanup on shutdown

        This method is final and should not be overridden.
        """
        try:
            print(f"Starting device {self.device_id} ({self.get_device_name()})", flush=True)

            # Connect to pipes first
            print("Connecting to named pipes...", flush=True)
            await self.connect_to_pipes()
            print("Connected to pipes successfully!", flush=True)

            # Start listening for commands
            await self.listen_for_commands()
        except Exception as e:
            print(f"Error in device: {e}", flush=True)
            import traceback
            traceback.print_exc()
        finally:
            print("Device shutting down", flush=True)
            self.cleanup_pipes()

    # =========================================================================
    # IPC Connection Management
    # =========================================================================

    async def connect_to_pipes(self):
        """
        Connect to both named pipes with retry logic.

        Attempts to connect up to 30 times with 1 second delays between attempts.
        """
        max_retries = 10
        retry_delay = 1.0

        for attempt in range(max_retries):
            try:
                print(f"Connection attempt {attempt + 1}/{max_retries}...", flush=True)

                if IS_WINDOWS:
                    await self._connect_pipes_windows()
                elif IS_LINUX:
                    await self._connect_pipes_linux()

                print("All pipes connected successfully!", flush=True)
                return

            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Connection failed (attempt {attempt + 1}): {e}. Retrying in {retry_delay}s...", flush=True)
                    await asyncio.sleep(retry_delay)
                else:
                    print(f"Failed to connect after {max_retries} attempts", flush=True)
                    raise Exception(f"Could not connect to named pipes after {max_retries} attempts: {e}")

    async def _connect_pipes_windows(self):
        """Windows-specific pipe connection using win32pipe."""
        # Try to connect to server-to-client pipe (we read from this)
        print(f"Connecting to pipe: {self.server_to_client_pipe}", flush=True)
        self.pipe_read_handle = win32file.CreateFile(
            self.server_to_client_pipe,
            win32file.GENERIC_READ,
            0,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )
        print("Read pipe connected!", flush=True)

        # Try to connect to client-to-server pipe (we write to this)
        print(f"Connecting to pipe: {self.client_to_server_pipe}", flush=True)
        self.pipe_write_handle = win32file.CreateFile(
            self.client_to_server_pipe,
            win32file.GENERIC_WRITE,
            0,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )
        print("Write pipe connected!", flush=True)

    async def _connect_pipes_linux(self):
        """Linux-specific pipe connection using UNIX domain sockets."""
        # Connect to server-to-client socket (we read from this)
        print(f"Connecting to socket: {self.server_to_client_pipe}", flush=True)
        self.read_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        # Wait for socket file to exist
        await self._wait_for_socket(self.server_to_client_pipe)
        self.read_socket.connect(self.server_to_client_pipe)
        print("Read socket connected!", flush=True)

        # Connect to client-to-server socket (we write to this)
        print(f"Connecting to socket: {self.client_to_server_pipe}", flush=True)
        self.write_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        await self._wait_for_socket(self.client_to_server_pipe)
        self.write_socket.connect(self.client_to_server_pipe)
        print("Write socket connected!", flush=True)

    async def _wait_for_socket(self, socket_path: str, timeout: float = 5.0):
        """
        Wait for socket file to exist.

        Args:
            socket_path: Path to the socket file
            timeout: Maximum time to wait in seconds

        Raises:
            TimeoutError: If socket file does not appear within timeout
        """
        start_time = time.time()
        while not os.path.exists(socket_path):
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Socket file not found: {socket_path}")
            await asyncio.sleep(0.1)

    def cleanup_pipes(self):
        """Close pipe handles and clean up resources."""
        try:
            if IS_WINDOWS:
                if self.pipe_read_handle:
                    win32file.CloseHandle(self.pipe_read_handle)
                    self.pipe_read_handle = None
                if self.pipe_write_handle:
                    win32file.CloseHandle(self.pipe_write_handle)
                    self.pipe_write_handle = None
            elif IS_LINUX:
                if self.read_socket:
                    self.read_socket.close()
                    self.read_socket = None
                if self.write_socket:
                    self.write_socket.close()
                    self.write_socket = None
        except Exception as e:
            print(f"Error cleaning up pipes: {e}", flush=True)

    # =========================================================================
    # Command Protocol Handling
    # =========================================================================

    async def listen_for_commands(self):
        """
        Listen for commands from Smart Home app.

        Continuously reads commands and dispatches them to appropriate handlers.
        """
        print("Starting command listener loop...", flush=True)

        while not self.should_stop:
            try:
                # Read command from Smart Home app
                print("Waiting for command from pipe...", flush=True)

                if IS_WINDOWS:
                    command = await self._read_command_windows()
                elif IS_LINUX:
                    command = await self._read_command_linux()

                if command:
                    print(f"Received command: {command}", flush=True)
                    await self.handle_command(command)
                else:
                    print("Received empty data, continuing...", flush=True)

            except Exception as e:
                print(f"Pipe error: {e}. Pipe may be broken.", flush=True)
                import traceback
                traceback.print_exc()
                break

    async def _read_command_windows(self) -> Optional[str]:
        """
        Read command from Windows named pipe.

        Returns:
            Command string, or None if no data
        """
        result, data = win32file.ReadFile(self.pipe_read_handle, 64*1024)
        if data:
            return data.decode('utf-8').strip()
        return None

    async def _read_command_linux(self) -> Optional[str]:
        """
        Read command from Linux UNIX socket.

        Returns:
            Command string, or None if no data
        """
        # Read data until we find a newline (commands are line-delimited)
        buffer = b''
        while b'\n' not in buffer:
            chunk = self.read_socket.recv(4096)
            if not chunk:
                raise ConnectionError("Socket closed by server")
            buffer += chunk

        # Extract the first command (up to newline)
        line, remainder = buffer.split(b'\n', 1)
        # Note: We're ignoring remainder for simplicity; in production you'd buffer it
        return line.decode('utf-8').strip()

    async def handle_command(self, command: str):
        """
        Process commands from Smart Home app.

        Routes commands to appropriate handler methods.

        Args:
            command: Command string from Smart Home app
        """
        try:
            if command == "INITIALIZE":
                await self.handle_initialize()
            elif command.startswith("SETPARAMETERS:"):
                await self.handle_set_parameters(command)
            elif command == "GETDATA_STRUCTURED":
                await self.handle_get_data_structured()
            elif command == "GETPARAMETERS":
                await self.handle_get_parameters()
            elif command == "CANCEL":
                await self.handle_cancel()
            elif command == "FINISH":
                await self.handle_finish()
            else:
                print(f"Unknown command: {command}", flush=True)

        except Exception as e:
            print(f"Error handling command {command}: {e}", flush=True)
            import traceback
            traceback.print_exc()

    # =========================================================================
    # Command Handlers
    # =========================================================================

    async def handle_initialize(self):
        """Handle INITIALIZE command - returns device name."""
        print("Initializing device...", flush=True)
        await asyncio.sleep(0.5)  # Simulate initialization
        device_name = self.get_device_name()
        await self.send_response(device_name)
        print(f"Device initialized: {device_name}", flush=True)

    async def handle_get_parameters(self):
        """Handle GETPARAMETERS command - returns parameter definitions."""
        print("Handling GETPARAMETERS request...", flush=True)

        parameters = await self.get_parameter_definitions()
        json_response = json.dumps(parameters)
        await self.send_response(f"PARAMETERS {json_response}")
        print("GETPARAMETERS response sent", flush=True)

    async def handle_set_parameters(self, command: str):
        """
        Handle SETPARAMETERS command - validates and stores parameters.

        Args:
            command: Full command string in format "SETPARAMETERS:{json}"
        """
        try:
            # Extract JSON from command: "SETPARAMETERS:{json}"
            json_part = command.split(":", 1)[1]
            parameters = json.loads(json_part)

            # Validate parameters using subclass implementation
            is_valid, error_message = self.validate_parameters(parameters)

            if not is_valid:
                print(f"Parameter validation failed: {error_message}", flush=True)
                await self.send_response("PARAMS_ERROR")
                return

            # Store validated parameters
            self.measurement_parameters = parameters
            print(f"Parameters set: {self.measurement_parameters}", flush=True)
            await self.send_response("PARAMS_SET")

        except Exception as e:
            print(f"Error setting parameters: {e}", flush=True)
            await self.send_response("PARAMS_ERROR")

    async def handle_get_data_structured(self):
        """Handle GETDATA_STRUCTURED command - generates and returns measurement data."""
        try:
            print("Generating measurement data LOL...", flush=True)
            print("doing stuff")
            # Generate data using subclass implementation
            data_points = await self.generate_measurement_data()
            print("Exited generate_measurement_data")
            # Create response in expected format
            response_data = {
                "rawData": [json.dumps(dp) for dp in data_points],  # Convert to string format
                "timestamp": datetime.now().isoformat(),
                "parameters": self.measurement_parameters
            }

            # Send as JSON
            json_response = json.dumps(response_data)
            print(f"Sending DATA response ({len(json_response)} bytes)...", flush=True)
            await self.send_response(f"DATA:{json_response}")
            print("Data sent successfully", flush=True)

        except Exception as e:
            print(f"Error generating data: {e}", flush=True)
            import traceback
            traceback.print_exc()
            await self.send_response("DATA_ERROR")

    async def handle_cancel(self):
        """Handle CANCEL command - cancels current measurement."""
        print("Measurement cancelled", flush=True)
        await self.send_response("CANCELLED")

    async def handle_finish(self):
        """Handle FINISH command - completes measurement and initiates shutdown."""
        print("Measurement finished, shutting down", flush=True)
        self.should_stop = True
        await self.send_response("FINISHED")

    # =========================================================================
    # Response Sending
    # =========================================================================

    async def send_response(self, response: str):
        """
        Send response back to Smart Home app.

        Args:
            response: Response string to send (newline will be added automatically)
        """
        try:
            # Write response with newline terminator
            response_bytes = (response + '\n').encode('utf-8')

            if IS_WINDOWS:
                win32file.WriteFile(self.pipe_write_handle, response_bytes)
            elif IS_LINUX:
                self.write_socket.sendall(response_bytes)

            # Log truncated response
            log_response = response[:100] + "..." if len(response) > 100 else response
            print(f"Sent response: {log_response}", flush=True)

        except Exception as e:
            print(f"Error sending response: {e}", flush=True)
            import traceback
            traceback.print_exc()
