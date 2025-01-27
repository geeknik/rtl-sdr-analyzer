"""
Signal detection and analysis module.
Implements algorithms for detecting and characterizing RF signals.
"""

import logging
import numpy as np
from datetime import datetime
from typing import Optional, List, Tuple
from .events import JammingEvent, DetectionStats

logger = logging.getLogger(__name__)

class SignalDetector:
    """Detects and analyzes RF signals in spectrum data."""
    
    def __init__(
        self,
        power_threshold: float = -70,
        bandwidth_threshold: float = 0.1e6,
        z_score_threshold: float = 1.5,
        detection_window: int = 5,
        min_duration: float = 0.1,
        test_mode: bool = False
    ):
        """
        Initialize detector with configuration parameters.
        
        Args:
            power_threshold: Minimum power level for detection (dB)
            bandwidth_threshold: Minimum bandwidth for detection (Hz)
            z_score_threshold: Z-score threshold for anomaly detection
            detection_window: Number of frames for detection window
            min_duration: Minimum event duration (seconds)
            test_mode: Enable more sensitive detection for testing
        """
        self.power_threshold = power_threshold
        self.bandwidth_threshold = bandwidth_threshold
        self.z_score_threshold = z_score_threshold
        self.detection_window = detection_window
        self.min_duration = min_duration
        self.test_mode = test_mode
        
        # Detection state
        self.power_history: List[float] = []
        self.baseline_mean: Optional[float] = None
        self.baseline_std: Optional[float] = None
        self.potential_signal = False
        self.signal_start_time: Optional[float] = None
        
        # Statistics
        self.stats = DetectionStats()
        
    def update_baseline(self, spectrum: np.ndarray) -> None:
        """
        Update baseline statistics for detection.
        
        Args:
            spectrum: Current power spectrum
        """
        current_mean = np.mean(spectrum)
        self.power_history.append(current_mean)
        
        if len(self.power_history) > self.detection_window:
            self.power_history.pop(0)
            
            if self.baseline_mean is None:
                self.baseline_mean = np.mean(self.power_history)
                self.baseline_std = np.std(self.power_history)
                logger.info("Baseline established: mean=%.2f dB, std=%.2f dB",
                          self.baseline_mean, self.baseline_std)
            else:
                # Update baseline with exponential moving average
                alpha = 0.1
                self.baseline_mean = ((1 - alpha) * self.baseline_mean + 
                                    alpha * current_mean)
                new_std = np.std(self.power_history)
                self.baseline_std = ((1 - alpha) * self.baseline_std + 
                                   alpha * new_std)
    
    def detect_signal(self, 
                     spectrum: np.ndarray, 
                     freq_range: np.ndarray,
                     timestamp: float) -> Optional[JammingEvent]:
        """
        Detect potential signals in the spectrum.
        
        Args:
            spectrum: Power spectrum data
            freq_range: Frequency range array
            timestamp: Current timestamp
            
        Returns:
            JammingEvent if signal detected, None otherwise
        """
        self.update_baseline(spectrum)
        
        if self.baseline_mean is None:
            return None
            
        # Calculate metrics
        max_power = np.max(spectrum)
        current_mean = np.mean(spectrum)
        z_score = ((current_mean - self.baseline_mean) / 
                  (self.baseline_std + 1e-10))
        
        # Calculate bandwidth
        mask = spectrum > (max_power - 3)
        bandwidth = np.sum(mask) * (freq_range[1] - freq_range[0]) * 1e6
        
        # Detection logic
        detection_criteria = [
            max_power > self.power_threshold,
            bandwidth > self.bandwidth_threshold,
            abs(z_score) > self.z_score_threshold
        ]
        
        is_signal = (all(detection_criteria) if not self.test_mode 
                    else any(detection_criteria))
        
        self.stats.update(max_power, is_signal)
        
        if is_signal and not self.potential_signal:
            self.potential_signal = True
            self.signal_start_time = timestamp
            logger.info(f"Potential signal detected: power={max_power:.2f}dB")
            
        elif is_signal and self.potential_signal:
            duration = timestamp - self.signal_start_time
            if duration >= self.min_duration:
                # Create event
                event = JammingEvent(
                    timestamp=datetime.fromtimestamp(timestamp),
                    frequency=freq_range[np.argmax(spectrum)],
                    power=max_power,
                    bandwidth=bandwidth,
                    duration=duration,
                    confidence=abs(z_score) / self.z_score_threshold,
                    snr=max_power - self.baseline_mean
                )
                logger.info(f"Signal confirmed: {event.to_dict()}")
                return event
                
        elif not is_signal and self.potential_signal:
            self.potential_signal = False
            self.signal_start_time = None
            logger.info("Signal ended")
            
        return None