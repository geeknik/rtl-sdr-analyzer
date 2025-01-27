import unittest
from unittest.mock import patch, MagicMock
import socket
import numpy as np
from src.core.rtlsdr_base import RTLSDRBase, RTLSDRException  # Replace with the correct import

class TestRTLSDRBase(unittest.TestCase):

    @patch('socket.socket')
    def test_connect_success(self, MockSocket):
        # Mock socket behavior for successful connection
        mock_socket_instance = MagicMock()
        MockSocket.return_value = mock_socket_instance
        
        rtl_sdr = RTLSDRBase(
            host='localhost', 
            port=1234, 
            center_freq=100e6
        )
        
        # Call the connect method
        rtl_sdr.connect()
        
        # Check if socket connection was established
        MockSocket.assert_called_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_socket_instance.connect.assert_called_with(('localhost', 1234))
        mock_socket_instance.setblocking.assert_called_with(0)
        
    @patch('socket.socket')
    def test_connect_failure(self, MockSocket):
        # Simulate socket error during connection
        MockSocket.side_effect = socket.error("Connection failed")
        
        rtl_sdr = RTLSDRBase(
            host='localhost', 
            port=1234, 
            center_freq=100e6
        )
        
        # Test if RTLSDRException is raised
        with self.assertRaises(RTLSDRException):
            rtl_sdr.connect()
        
    @patch('socket.socket')
    def test_read_samples_success(self, MockSocket):
        # Mock socket behavior for receiving data
        mock_socket_instance = MagicMock()
        MockSocket.return_value = mock_socket_instance
        
        # Simulate receiving raw data
        raw_data = np.random.randint(0, 256, 2 * 1024 * 64, dtype=np.uint8).tobytes()
        mock_socket_instance.recv.return_value = raw_data
        
        rtl_sdr = RTLSDRBase(
            host='localhost', 
            port=1234, 
            center_freq=100e6, 
            sample_rate=2.048e6,
            fft_size=1024
        )
        
        rtl_sdr.sock = mock_socket_instance
        
        # Call the read_samples method
        samples = rtl_sdr.read_samples()
        
        # Check if we received the correct number of samples
        self.assertEqual(samples.shape[0], 1024)
        
    @patch('socket.socket')
    def test_read_samples_no_data(self, MockSocket):
        # Mock socket behavior for no data available
        mock_socket_instance = MagicMock()
        MockSocket.return_value = mock_socket_instance
        
        # Simulate receiving no data
        mock_socket_instance.recv.return_value = b''
        
        rtl_sdr = RTLSDRBase(
            host='localhost', 
            port=1234, 
            center_freq=100e6, 
            sample_rate=2.048e6,
            fft_size=1024
        )
        
        rtl_sdr.sock = mock_socket_instance
        
        # Call the read_samples method
        samples = rtl_sdr.read_samples()
        
        # Ensure that the returned samples are None
        self.assertIsNone(samples)
        
    @patch('socket.socket')
    def test_send_command_failure(self, MockSocket):
        # Simulate a socket error during command sending
        mock_socket_instance = MagicMock()
        MockSocket.return_value = mock_socket_instance
        
        rtl_sdr = RTLSDRBase(
            host='localhost', 
            port=1234, 
            center_freq=100e6, 
            sample_rate=2.048e6,
            fft_size=1024
        )
        
        rtl_sdr.sock = mock_socket_instance
        
        # Simulate a socket error when sending command
        mock_socket_instance.send.side_effect = socket.error("Send failed")
        
        # Test if RTLSDRException is raised
        with self.assertRaises(RTLSDRException):
            rtl_sdr._send_command(0x01, int(100e6))
        
    @patch('socket.socket')
    def test_cleanup(self, MockSocket):
        # Test cleanup behavior when closing the socket
        mock_socket_instance = MagicMock()
        MockSocket.return_value = mock_socket_instance
        
        rtl_sdr = RTLSDRBase(
            host='localhost', 
            port=1234, 
            center_freq=100e6
        )
        
        rtl_sdr.sock = mock_socket_instance
        
        # Call cleanup manually
        rtl_sdr._cleanup()
        
        # Verify that the socket was closed
        mock_socket_instance.close.assert_called_once()
        
    @patch('socket.socket')
    def test_device_configuration_failure(self, MockSocket):
        # Simulate failure during device configuration
        mock_socket_instance = MagicMock()
        MockSocket.return_value = mock_socket_instance
        
        rtl_sdr = RTLSDRBase(
            host='localhost', 
            port=1234, 
            center_freq=100e6, 
            sample_rate=2.048e6,
            fft_size=1024
        )
        
        rtl_sdr.sock = mock_socket_instance
        
        # Simulate an error during device configuration
        rtl_sdr._send_command = MagicMock(side_effect=RTLSDRException("Configuration error"))
        
        # Test if RTLSDRException is raised during the configuration
        with self.assertRaises(RTLSDRException):
            rtl_sdr.connect()

if __name__ == '__main__':
    unittest.main()
