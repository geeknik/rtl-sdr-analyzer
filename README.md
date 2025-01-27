# RTL-SDR Signal Analyzer and Jamming Detector

A real-time spectrum analyzer and signal detection tool using RTL-SDR hardware. This project provides capabilities for monitoring radio frequency spectrum and detecting potential signal anomalies or jamming events.

## Features

- Real-time spectrum visualization with waterfall display
- Automatic signal detection and analysis
- Dynamic baseline calculation and adaptation
- Configurable detection parameters
- Network-based RTL-SDR support (RTL-TCP)

## Requirements

- Python 3.8+
- RTL-SDR hardware
- RTL-TCP server running

## Installation

1. Clone the repository:
```bash
git clone https://github.com/msalexms/rtl-sdr-analyzer.git
cd rtl-sdr-analyzer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start your RTL-TCP server with [docker compose file](docker/docker-compose.yml):

```bash
cd docker
docker-compose up -d
```

2. Run the analyzer:
```bash
python scripts/run_analyzer.py --freq 915e6 --sample-rate 2.048e6
```

### Command Line Arguments

- `--host`: RTL-TCP server host (default: 192.168.100.248)
- `--port`: RTL-TCP server port (default: 1234)
- `--freq`: Center frequency in Hz (required)
- `--sample-rate`: Sample rate in Hz (default: 2.048e6)
- `--fft-size`: FFT size (default: 2048)
- `--waterfall-length`: Waterfall display length (default: 50)

## Configuration

Detection parameters can be adjusted in `src/detection/detector.py`:

- Power threshold
- Bandwidth threshold
- Z-score threshold
- Detection window
- Minimum duration

## Plot example

In the image below we can see an example of the spectrogram on frequency 446 while pressing the transmit button on a walkie talkie.

![446 mHz](spectrogram.png)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
