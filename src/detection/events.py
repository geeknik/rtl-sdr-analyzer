"""
Event data structures for signal detection and analysis.
Defines the core data classes used to represent detection events.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class JammingEvent:
    """Represents a detected signal event."""
    timestamp: datetime
    frequency: float
    power: float
    bandwidth: float
    duration: float
    confidence: float
    
    # Optional metadata
    snr: Optional[float] = None
    center_offset: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert event to dictionary format for logging/storage."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'frequency': round(self.frequency, 3),
            'power': round(self.power, 2),
            'bandwidth': round(self.bandwidth, 2),
            'duration': round(self.duration, 2),
            'confidence': round(self.confidence, 2),
            'snr': round(self.snr, 2) if self.snr is not None else None,
            'center_offset': round(self.center_offset, 2) if self.center_offset is not None else None
        }

@dataclass
class DetectionStats:
    """Statistics for signal detection performance."""
    total_frames: int = 0
    detected_frames: int = 0
    false_positives: int = 0
    detection_rate: float = 0.0
    average_power: float = 0.0
    peak_power: float = 0.0
    
    def update(self, power: float, is_detection: bool) -> None:
        """Update detection statistics."""
        self.total_frames += 1
        if is_detection:
            self.detected_frames += 1
        self.peak_power = max(self.peak_power, power)
        self.average_power = (
            (self.average_power * (self.total_frames - 1) + power) / 
            self.total_frames
        )
        self.detection_rate = self.detected_frames / self.total_frames