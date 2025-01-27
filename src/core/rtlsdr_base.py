"""
RTL-SDR Base Module
Handles the core RTL-SDR functionality including device connection, configuration,
and sample acquisition with proper error handling and logging.
"""

import logging
import socket
import struct
from typing import Optional, Tuple
import numpy as np
from scipy.signal.windows import blackmanharris

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RTLSDRException(Exception):
    """Custom exception for RTL-SDR related errors."""
    pass

class RTLSDRBase:
    """Base class for RTL-SDR operations with robust error handling."""
    
    def __init__(
        self,
        host: str,
        port: int,
        center_freq: float,
        sample_rate: float = 2.048e6,
        fft_size: int = 1024
    ):
        """
        Initialize RTL-SDR connection parameters.
        
        Args:
            host: RTL-TCP server hostname
            port: RTL-TCP server port
            center_freq: Center frequency in Hz
            sample_rate: Sample rate in Hz
            fft_size: FFT size for spectrum analysis
        """
        self.host = host
        self.port = port
        self.center_freq = center_freq
        self.sample_rate = sample_rate
        self.fft_size = fft_size
        self.sock: Optional[socket.socket] = None
        self.window = blackmanharris(fft_size)
        
        # Calculate frequency range
        self.freq_range = np.linspace(
            -sample_rate/2e6 + center_freq/1e6,
            sample_rate/2e6 + center_freq/1e6,
            fft_size
        )
        
    def connect(self) -> None:
        """
        Establish connection to RTL-TCP server with error handling.
        
        Raises:
            RTLSDRException: If connection fails
        """
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 1024*1024)
           # self.sock.settimeout(5.0)  # 5 second timeout
            
            logger.info(f"Connecting to RTL-TCP server at {self.host}:{self.port}")
            self.sock.connect((self.host, self.port))
            self.sock.setblocking(0)
            
            # Configure device
            self._configure_device()
            logger.info("Successfully connected to RTL-TCP server")
            
        except socket.error as e:
            self._cleanup()
            raise RTLSDRException(f"Failed to connect to RTL-TCP server: {str(e)}")
            
    def _configure_device(self) -> None:
        """
        Configure RTL-SDR device parameters.
        
        Raises:
            RTLSDRException: If configuration fails
        """
        try:
            commands = [
                (0x01, int(self.center_freq)),  # Set frequency
                (0x02, int(self.sample_rate)),  # Set sample rate
                (0x03, 0),                      # Set gain mode (auto)
                (0x05, 0),                      # Set AGC mode
                (0x08, 1)                       # Set direct sampling mode
            ]
            
            for cmd, value in commands:
                self._send_command(cmd, value)
                
        except Exception as e:
            raise RTLSDRException(f"Failed to configure device: {str(e)}")
    
    def _send_command(self, command: int, value: int) -> None:
        """
        Send command to RTL-SDR device.
        
        Args:
            command: Command number
            value: Command value
        """
        if self.sock is None:
            raise RTLSDRException("No connection to RTL-TCP server")
            
        try:
            self.sock.send(struct.pack('>BI', command, value))
        except socket.error as e:
            raise RTLSDRException(f"Failed to send command: {str(e)}")
    
    def read_samples(self) -> Optional[np.ndarray]:
        """
        Read samples from RTL-SDR device with error handling.
        
        Returns:
            Complex numpy array of samples or None if no data available
        """
        if self.sock is None:
            raise RTLSDRException("No connection to RTL-TCP server")
            
        try:
            raw_data = self.sock.recv(self.fft_size * 2 * 64)
            if not raw_data:
                return None
                
            # Convert to complex samples
            data = np.frombuffer(raw_data, dtype=np.uint8).reshape(-1, 2)
            iq = ((data[:, 0] + 1j * data[:, 1]) - 127.5 - 127.5j) / 127.5
            
            # Handle sample size
            if len(iq) >= self.fft_size:
                logger.debug("Received samples")
                return iq[:self.fft_size]
            else:
                padded = np.zeros(self.fft_size, dtype=complex)
                padded[:len(iq)] = iq
                logger.debug("Received partial samples")
                return padded
                
        except socket.error as e:
            if e.errno != 10035:  # Ignore "would block" error
                logger.error(f"Error reading samples: {str(e)}")
            return None
            
    def _cleanup(self) -> None:
        """Clean up resources."""
        if self.sock:
            try:
                self.sock.close()
                logger.info("Closed RTL-TCP connection")
            except Exception as e:
                logger.error(f"Error during cleanup: {str(e)}")
            finally:
                self.sock = None
                
    def __del__(self) -> None:
        """Destructor to ensure cleanup."""
        self._cleanup()