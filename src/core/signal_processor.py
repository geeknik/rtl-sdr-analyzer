"""
Signal Processing Module
Handles all signal processing operations including FFT, filtering,
and power calculations with proper error handling.
"""

import logging
from typing import Optional, Tuple
import numpy as np
from scipy.fft import fft, fftshift
from scipy.signal import butter, filtfilt

logger = logging.getLogger(__name__)

class SignalProcessor:
    """Handles signal processing operations for RTL-SDR data."""
    
    def __init__(self, fft_size: int, sample_rate: float):
        """
        Initialize signal processor.
        
        Args:
            fft_size: Size of FFT operation
            sample_rate: Sample rate in Hz
        """
        self.fft_size = fft_size
        self.sample_rate = sample_rate
        
        # Pre-compute filter coefficients
        self.filter_coeffs = self._create_filter()
        
    def _create_filter(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create Butterworth filter coefficients.
        
        Returns:
            Tuple of filter numerator and denominator coefficients
        """
        nyquist = 0.5 * self.fft_size
        cutoff = 0.1 * nyquist
        return butter(4, cutoff/nyquist)
        
    def process_samples(self, iq_data: np.ndarray) -> Optional[np.ndarray]:
        """
        Process IQ samples into power spectrum.
        
        Args:
            iq_data: Complex IQ samples
            
        Returns:
            Power spectrum in dB or None if processing fails
        """
        try:
            if iq_data is None or len(iq_data) != self.fft_size:
                return None
                
            # Remove DC offset
            iq_data -= np.mean(iq_data)
            
            # Compute FFT
            fft_data = fftshift(fft(iq_data))
            
            # Calculate power spectrum
            power_db = 20 * np.log10(np.abs(fft_data) + 1e-12)
            
            # Apply filtering
            power_db_smooth = filtfilt(self.filter_coeffs[0], 
                                     self.filter_coeffs[1], 
                                     power_db)
            
            return power_db_smooth
            
        except Exception as e:
            logger.error(f"Error processing samples: {str(e)}")
            return None
            
    def calculate_signal_metrics(self, 
                               spectrum: np.ndarray,
                               freq_range: np.ndarray) -> dict:
        """
        Calculate various signal metrics from the spectrum.
        
        Args:
            spectrum: Power spectrum in dB
            freq_range: Frequency range array
            
        Returns:
            Dictionary containing signal metrics
        """
        try:
            metrics = {
                'max_power': np.max(spectrum),
                'mean_power': np.mean(spectrum),
                'peak_frequency': freq_range[np.argmax(spectrum)],
                'bandwidth': self._calculate_bandwidth(spectrum, freq_range)
            }
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            return {}
            
    def _calculate_bandwidth(self, 
                           spectrum: np.ndarray,
                           freq_range: np.ndarray) -> float:
        """
        Calculate 3dB bandwidth of the strongest signal.
        
        Args:
            spectrum: Power spectrum in dB
            freq_range: Frequency range array
            
        Returns:
            Bandwidth in Hz
        """
        try:
            max_power = np.max(spectrum)
            mask = spectrum > (max_power - 3)  # 3dB bandwidth
            return np.sum(mask) * (freq_range[1] - freq_range[0]) * 1e6
            
        except Exception as e:
            logger.error(f"Error calculating bandwidth: {str(e)}")
            return 0.0