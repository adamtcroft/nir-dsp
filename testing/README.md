# JSFX Testing Framework

A Python-based testing framework for JSFX audio effects. This framework allows automated testing of JSFX plugins by rendering audio through REAPER and analyzing the results.

## Overview

The testing framework solves a critical challenge: how to automatically verify that JSFX effects work correctly without manual listening. It does this by:

1. **Generating test signals** (impulses, sine waves, sweeps, noise)
2. **Rendering audio through JSFX effects** using REAPER's command-line rendering
3. **Analyzing the output** using FFT and other signal processing techniques
4. **Comparing results** to verify expected behavior

## Requirements

- Python 3.7+
- NumPy
- REAPER (with `reaper` command available in PATH)
- JSFX effects to test

## Components

### 1. Signal Generator (`signal_generator.py`)

Generates various test audio signals:

- **Impulse**: Single-sample peak for impulse response testing
- **Sine waves**: Pure tones at specific frequencies
- **Frequency sweeps**: Logarithmic or linear chirps for frequency response analysis
- **White noise**: Random noise for general testing

**Example usage:**
```python
from signal_generator import SignalGenerator

gen = SignalGenerator(sample_rate=48000, duration=2.0)
sine = gen.generate_sine(frequency=1000, amplitude=0.5)
gen.save_wav(sine, "test_1000hz.wav")
```

### 2. REAPER Project Generator (`reaper_project.py`)

Creates REAPER project files (.rpp) programmatically with:

- Audio tracks with media files
- JSFX effects with configurable slider values
- Proper render settings

**Example usage:**
```python
from reaper_project import create_test_project

create_test_project(
    jsfx_path="LowPassFilter.jsfx",
    input_wav="test_signals/sine_1000hz.wav",
    output_rpp="test_projects/test.rpp",
    slider_values={"frequencySlider": 500}
)
```

### 3. JSFX Tester (`jsfx_tester.py`)

Main testing framework with two key classes:

#### AudioAnalyzer

Analyzes rendered audio files:

- `read_wav()`: Load WAV files as numpy arrays
- `measure_rms()`: Measure RMS level
- `measure_peak()`: Measure peak level
- `measure_frequency_response()`: Measure amplitude at specific frequency using FFT

#### JSFXTester

Orchestrates testing:

- `render_with_effect()`: Render audio through a JSFX effect
- `test_frequency_response()`: Test effect at multiple frequencies

**Example usage:**
```python
from jsfx_tester import JSFXTester

tester = JSFXTester()
results = tester.test_frequency_response(
    jsfx_path="LowPassFilter.jsfx",
    test_frequencies=[100, 500, 1000, 2000, 5000],
    slider_values={"frequencySlider": 1000}
)

for freq, data in results.items():
    print(f"{freq} Hz: {data['attenuation_db']:.2f} dB")
```

## Usage

### Quick Start

1. **Run the example test:**
```bash
cd testing
python test_lowpass_example.py
```

This will test the LowPassFilter.jsfx at multiple cutoff frequencies and display the results.

### Writing Your Own Tests

```python
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from jsfx_tester import JSFXTester

# Initialize tester
tester = JSFXTester()

# Test your effect
results = tester.test_frequency_response(
    jsfx_path="path/to/your/effect.jsfx",
    test_frequencies=[100, 1000, 10000],
    slider_values={"slider1": 50, "slider2": 0.5},
    sample_rate=48000
)

# Verify results
for freq, data in results.items():
    atten_db = data['attenuation_db']
    if atten_db < -20:
        print(f"PASS: {freq} Hz properly attenuated")
    else:
        print(f"FAIL: {freq} Hz not attenuated enough")
```

### Custom Signal Generation

```python
from signal_generator import SignalGenerator

# Create custom test signal
gen = SignalGenerator(sample_rate=48000, duration=5.0)
sweep = gen.generate_sweep(f_start=20, f_end=20000)
gen.save_wav(sweep, "my_sweep.wav")

# Use with tester
tester.render_with_effect(
    jsfx_path="MyEffect.jsfx",
    input_wav="my_sweep.wav",
    output_wav="output.wav",
    slider_values={"gain": -6}
)
```

## Directory Structure

```
testing/
├── README.md                    # This file
├── signal_generator.py          # Test signal generation
├── reaper_project.py            # REAPER project file generator
├── jsfx_tester.py              # Main testing framework
├── test_lowpass_example.py     # Example test script
├── test_signals/               # Generated test signals (created on demand)
├── test_projects/              # Generated .rpp files (temporary)
└── test_output/                # Rendered output files (temporary)
```

## How It Works

1. **Test signal creation**: Python generates a WAV file with known characteristics
2. **Project generation**: Python creates a .rpp file that loads the test signal and applies the JSFX effect
3. **Rendering**: REAPER is invoked with `-renderproject` to render the audio offline
4. **Analysis**: Python reads the rendered WAV and analyzes it using FFT and other techniques
5. **Verification**: Results are compared against expected behavior

## Testing Philosophy

Since you (the AI agent) cannot hear audio, the framework uses objective measurements:

- **Frequency response**: Measure attenuation/gain at specific frequencies
- **RMS levels**: Verify overall signal level
- **Peak levels**: Check for clipping or unexpected peaks
- **Impulse response**: Analyze filter characteristics

These measurements allow automated verification without subjective listening.

## Limitations

- **REAPER must be installed** and accessible via command line
- **Rendering is slower** than real-time (but automated)
- **Only objective measurements** - can't detect subjective quality issues
- **Slider values use internal names** - must match JSFX slider variable names

## Future Improvements

Potential enhancements (not yet implemented):

- Phase response measurement
- THD (Total Harmonic Distortion) analysis
- Intermodulation distortion testing
- Automated testing of multiple effects in batch
- Visual plots of frequency response curves
- Integration with CI/CD systems

## Troubleshooting

**REAPER not found:**
- Ensure REAPER is installed
- Add REAPER to your PATH
- Or pass `reaper_command="/path/to/reaper"` to JSFXTester

**No rendered output:**
- Check that JSFX path is correct
- Verify slider names match JSFX variable names
- Check REAPER error messages in stderr

**Import errors:**
- Make sure NumPy is installed: `pip install numpy`
- Use absolute paths or add testing directory to sys.path

## License

(C) 2026 NIR, LLC - All Rights Reserved
