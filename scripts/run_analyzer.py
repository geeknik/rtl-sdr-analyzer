"""
Main script to run the RTL-SDR analyzer.
"""

import sys
import time
import logging
import argparse
import signal
from pathlib import Path
import yaml
from datetime import datetime

# Add src to Python path
src_path = Path(__file__).resolve().parent.parent / 'src'
sys.path.append(str(src_path))

from src.core.rtlsdr_base import RTLSDRBase, RTLSDRException
from src.core.signal_processor import SignalProcessor
from src.detection.detector import SignalDetector
from src.visualization.plotter import SpectrumPlotter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SignalAnalyzer:
    """Main class coordinating all components."""
    
    def __init__(self, config: dict):
        """Initialize analyzer with configuration."""
        self.config = config
        self.running = False
        
        # Initialize components
        self.rtlsdr = RTLSDRBase(
            host=config['rtl_tcp']['host'],
            port=config['rtl_tcp']['port'],
            center_freq=config['receiver']['frequency'],
            sample_rate=config['receiver']['sample_rate'],
            fft_size=config['receiver']['fft_size']
        )
        
        self.processor = SignalProcessor(
            fft_size=config['receiver']['fft_size'],
            sample_rate=config['receiver']['sample_rate']
        )
        
        self.detector = SignalDetector(
            power_threshold=config['detector']['power_threshold'],
            bandwidth_threshold=config['detector']['bandwidth_threshold'],
            z_score_threshold=config['detector']['z_score_threshold'],
            detection_window=config['detector']['detection_window'],
            min_duration=config['detector']['min_duration'],
            test_mode=config['detector']['test_mode']
        )
        
        self.plotter = SpectrumPlotter(
            freq_range=self.rtlsdr.freq_range,
            waterfall_length=config['display']['waterfall_length'],
            update_interval=config['display']['update_interval']
        )
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        
    def handle_signal(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("Shutdown signal received")
        self.stop()
            
    def update(self, frame):
        """Update function for visualization."""
        if not self.running:
            return self.plotter.get_artists()  # Return artists even when not running
            
        try:
            # Read and process samples
            iq_data = self.rtlsdr.read_samples()
            if iq_data is not None:
                spectrum = self.processor.process_samples(iq_data)
                if spectrum is not None:
                    event = self.detector.detect_signal(
                        spectrum,
                        self.rtlsdr.freq_range,
                        time.time()
                    )
                    return self.plotter.update(spectrum, event)
            
            # Return current artists if no new data
            return self.plotter.get_artists()
                
        except Exception as e:
            logger.error(f"Error in update loop: {str(e)}")
            self.stop()
            return self.plotter.get_artists()
        
    def start(self):
        """Start the analyzer."""
        self.running = True
        self.rtlsdr.connect()
        logger.info("Starting signal analyzer...")
        
        # Start visualization
        self.plotter.start(self.update)
            
            
    def stop(self):
        """Stop the analyzer and cleanup."""
        self.running = False
        logger.info("Stopping signal analyzer...")
        
        # Cleanup components
        try:
            self.plotter.stop()
            self.rtlsdr._cleanup()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            
        sys.exit(0)


def load_config(config_path: str = None) -> dict:
    """Load configuration from file or use defaults."""
    default_config = {
        'rtl_tcp': {
            'host': '192.168.31.34',
            'port': 1234
        },
        'receiver': {
            'frequency': 915e6,
            'sample_rate': 2.048e6,
            'fft_size': 2048
        },
        'detector': {
            'power_threshold': -70,
            'bandwidth_threshold': 0.1e6,
            'z_score_threshold': 1.5,
            'detection_window': 5,
            'min_duration': 0.1,
            'test_mode': False
        },
        'display': {
            'waterfall_length': 50,
            'update_interval': 1
        }
    }
    
    if config_path and Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                # Merge user config with defaults
                for section in default_config:
                    if section in user_config:
                        default_config[section].update(user_config[section])
        except Exception as e:
            logger.error(f"Error loading config file: {str(e)}")
            
    return default_config

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='RTL-SDR Signal Analyzer and Detector'
    )
    parser.add_argument(
        '--config',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--freq',
        type=float,
        help='Center frequency in Hz (overrides config)'
    )
    parser.add_argument(
        '--host',
        help='RTL-TCP server host (overrides config)'
    )
    parser.add_argument(
        '--port',
        type=int,
        help='RTL-TCP server port (overrides config)'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Override config with command line arguments
    if args.freq:
        config['receiver']['frequency'] = args.freq
    if args.host:
        config['rtl_tcp']['host'] = args.host
    if args.port:
        config['rtl_tcp']['port'] = args.port
        
    # Start analyzer
    analyzer = SignalAnalyzer(config)
    analyzer.start()

if __name__ == '__main__':
    main()