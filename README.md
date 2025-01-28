<div align="center">

# 📡 RTL-SDR Signal Analyzer & Jamming Detector

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![RTL-SDR](https://img.shields.io/badge/RTL--SDR-Compatible-orange.svg)](https://www.rtl-sdr.com)

*A real-time spectrum analyzer and signal detection tool leveraging RTL-SDR hardware for RF monitoring and jamming detection.*

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Configuration](#%EF%B8%8F-configuration) • [Contributing](#-contributing)

</div>

---

## ✨ Features

- 📊 **Real-time Visualization**: Advanced spectrum analysis with waterfall display
- 🔍 **Smart Detection**: Automatic signal anomaly and jamming detection
- 📈 **Dynamic Analysis**: Adaptive baseline calculation and threshold adjustment
- ⚙️ **Flexible Configuration**: Fully customizable detection parameters
- 🌐 **Network Support**: Built-in RTL-TCP compatibility for remote operation

## 🚀 Installation

### Prerequisites

Before you begin, ensure you have:
- Python 3.8 or newer
- RTL-SDR hardware
- Active RTL-TCP server ([docker-compose.yml](docker/docker-compose.yml))

### Setup

```bash
# Clone the repository
git clone https://github.com/msalexms/rtl-sdr-analyzer.git
cd rtl-sdr-analyzer

# Install required packages
pip install -r requirements.txt
```

## 💻 Usage

1. Start the RTL-TCP server:
```bash
cd docker
docker-compose up -d
```

2. Launch the analyzer:
```bash
python scripts/run_analyzer.py --freq 915e6 --sample-rate 2.048e6
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--host` | RTL-TCP server host | 192.168.100.248 |
| `--port` | RTL-TCP server port | 1234 |
| `--freq` | Center frequency (Hz) | *Required* |
| `--sample-rate` | Sample rate (Hz) | 2.048e6 |
| `--fft-size` | FFT size | 2048 |
| `--waterfall-length` | Waterfall display length | 50 |

### With config file
You alternative can run it with the [config.yml](config.yml) file.

```bash
python scripts/run_analyzer.py --config path/to/config.yml
```

> :warning: **Problesm with imports**: Run the script updating the python path: PYTHONPATH=$PYTHONPATH:/path/to/your/rtl-sdr-analyzer

## ⚙️ Configuration

Detection parameters can be customized in `src/detection/detector.py`:

```python
{
    'power_threshold': -70,      # Signal power threshold (dB)
    'bandwidth_threshold': 0.1e6, # Minimum signal bandwidth (Hz)
    'z_score_threshold': 1.5,    # Statistical deviation threshold
    'detection_window': 5,       # Analysis window (seconds)
    'min_duration': 0.1         # Minimum event duration (seconds)
}
```

## 📊 Signal Analysis Examples

### Walkie-Talkie Transmission (446 MHz)
![446 MHz Spectrogram](spectrogram.png)
*Spectrogram showing distinct signal patterns during walkie-talkie transmission at 446 MHz*

### Common Signal Patterns
- 📱 **GSM/LTE**: Characteristic wide-band signals
- 📻 **FM Radio**: Strong, stable signals in the 88-108 MHz range
- 🛜 **Wi-Fi**: Periodic bursts in the 2.4/5 GHz bands
- 🎮 **RF Remote Controls**: Brief, narrow-band transmissions

## 🤝 Contributing

We welcome contributions! To contribute:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
<p>Developed with ❤️ by RF enthusiasts</p>

[Report Bug](https://github.com/msalexms/rtl-sdr-analyzer/issues) • [Request Feature](https://github.com/msalexms/rtl-sdr-analyzer/issues)
</div>
