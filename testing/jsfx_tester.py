#!/usr/bin/env python3
"""
JSFX testing framework.
Provides tools to test JSFX effects by rendering audio through REAPER
and analyzing the results.
"""

import subprocess
import wave
import struct
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import tempfile
import shutil

from signal_generator import SignalGenerator
from reaper_project import create_test_project


class AudioAnalyzer:
    """Analyze rendered audio files for testing."""
    
    @staticmethod
    def read_wav(filename):
        """
        Read WAV file and return samples as numpy array.
        
        Args:
            filename: Path to WAV file
            
        Returns:
            Tuple of (samples, sample_rate, channels)
            samples is numpy array of shape (num_samples, channels)
        """
        with wave.open(str(filename), 'r') as wav:
            sample_rate = wav.getframerate()
            num_channels = wav.getnchannels()
            num_frames = wav.getnframes()
            
            # Read all frames
            raw_data = wav.readframes(num_frames)
            
            # Convert to numpy array
            if wav.getsampwidth() == 2:  # 16-bit
                samples = np.frombuffer(raw_data, dtype=np.int16)
            elif wav.getsampwidth() == 4:  # 32-bit float
                samples = np.frombuffer(raw_data, dtype=np.float32)
            else:
                raise ValueError(f"Unsupported sample width: {wav.getsampwidth()}")
            
            # Reshape to (num_samples, channels)
            samples = samples.reshape(-1, num_channels)
            
            # Convert to float -1.0 to 1.0 range
            if samples.dtype == np.int16:
                samples = samples.astype(np.float32) / 32768.0
            
            return samples, sample_rate, num_channels
    
    @staticmethod
    def measure_rms(samples, start_sec=0, end_sec=None):
        """
        Measure RMS (root mean square) level.
        
        Args:
            samples: numpy array of audio samples
            start_sec: Start time in seconds (default 0)
            end_sec: End time in seconds (default None = end of file)
            
        Returns:
            RMS value (linear, not dB)
        """
        if end_sec is None:
            end_sec = len(samples)
        
        return np.sqrt(np.mean(samples[int(start_sec):int(end_sec)]**2))
    
    @staticmethod
    def measure_peak(samples):
        """
        Measure peak level.
        
        Args:
            samples: numpy array of audio samples
            
        Returns:
            Peak value (linear, not dB)
        """
        return np.max(np.abs(samples))
    
    @staticmethod
    def measure_frequency_response(samples, sample_rate, target_freq, window_sec=0.5):
        """
        Measure the amplitude of a specific frequency in the signal.
        Uses FFT to analyze frequency content.
        
        Args:
            samples: numpy array of audio samples
            sample_rate: Sample rate in Hz
            target_freq: Frequency to measure in Hz
            window_sec: Analysis window duration in seconds
            
        Returns:
            Amplitude at target frequency (linear)
        """
        # Take middle portion of signal for analysis
        total_samples = len(samples)
        window_samples = int(window_sec * sample_rate)
        start = max(0, (total_samples - window_samples) // 2)
        end = start + window_samples
        
        # Use first channel if stereo
        if len(samples.shape) > 1:
            signal = samples[start:end, 0]
        else:
            signal = samples[start:end]
        
        # Apply window to reduce spectral leakage
        window = np.hanning(len(signal))
        signal_windowed = signal * window
        
        # Perform FFT
        fft = np.fft.rfft(signal_windowed)
        freqs = np.fft.rfftfreq(len(signal_windowed), 1/sample_rate)
        
        # Find closest frequency bin
        freq_idx = np.argmin(np.abs(freqs - target_freq))
        
        # Return amplitude (normalized by window and FFT size)
        amplitude = np.abs(fft[freq_idx]) / (len(signal_windowed) / 2)
        
        return amplitude
    
    @staticmethod
    def linear_to_db(linear_value):
        """Convert linear amplitude to dB."""
        if linear_value <= 0:
            return -np.inf
        return 20 * np.log10(linear_value)
    
    @staticmethod
    def db_to_linear(db_value):
        """Convert dB to linear amplitude."""
        return 10 ** (db_value / 20)


class JSFXTester:
    """Test JSFX effects by rendering through REAPER."""
    
    def __init__(self, reaper_command="reaper", effects_dir=None):
        """
        Initialize JSFX tester.
        
        Args:
            reaper_command: Command to run REAPER (default "reaper")
            effects_dir: Directory containing JSFX effects (default None = use REAPER default)
        """
        self.reaper_command = reaper_command
        self.effects_dir = effects_dir
        self.analyzer = AudioAnalyzer()
        
    def render_with_effect(self, jsfx_path, input_wav, output_wav, 
                          slider_values=None, sample_rate=48000):
        """
        Render audio through a JSFX effect.
        
        Args:
            jsfx_path: Path to JSFX effect file
            input_wav: Path to input WAV file
            output_wav: Path for output WAV file
            slider_values: Dict of slider values
            sample_rate: Sample rate
            
        Returns:
            Path to rendered output file
        """
        # Create temporary project file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rpp', delete=False) as tmp:
            project_file = tmp.name
        
        try:
            # Generate project
            create_test_project(
                jsfx_path=jsfx_path,
                input_wav=input_wav,
                output_rpp=project_file,
                slider_values=slider_values,
                sample_rate=sample_rate
            )
            
            # Prepare output path
            output_path = Path(output_wav)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Render project
            cmd = [
                self.reaper_command,
                "-nosplash",
                "-renderproject", project_file,
                "-saveas", str(output_path.with_suffix('.rpp')),
                "-close:nosave:exit"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # REAPER renders to the project directory with a specific pattern
            # We need to find and move the rendered file
            project_dir = Path(project_file).parent
            rendered_files = list(project_dir.glob("*.wav"))
            
            if rendered_files:
                # Move the first rendered file to our desired output location
                shutil.move(str(rendered_files[0]), str(output_path))
                return output_path
            else:
                raise RuntimeError(f"No rendered output found. REAPER stderr: {result.stderr}")
                
        finally:
            # Clean up temporary project file
            Path(project_file).unlink(missing_ok=True)
    
    def test_frequency_response(self, jsfx_path, test_frequencies, 
                                slider_values=None, sample_rate=48000):
        """
        Test frequency response of a JSFX effect at multiple frequencies.
        
        Args:
            jsfx_path: Path to JSFX effect
            test_frequencies: List of frequencies to test (Hz)
            slider_values: Dict of slider values
            sample_rate: Sample rate
            
        Returns:
            Dict mapping frequency -> dict with 'input_level', 'output_level', 'attenuation_db'
        """
        results = {}
        
        for freq in test_frequencies:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir = Path(tmpdir)
                
                # Generate test signal
                gen = SignalGenerator(sample_rate=sample_rate, duration=2.0)
                input_signal = gen.generate_sine(freq, amplitude=0.5)
                input_wav = tmpdir / f"input_{freq}hz.wav"
                gen.save_wav(input_signal, input_wav)
                
                # Measure input level
                input_samples, _, _ = self.analyzer.read_wav(input_wav)
                input_level = self.analyzer.measure_frequency_response(
                    input_samples, sample_rate, freq
                )
                
                # Render through effect
                output_wav = tmpdir / f"output_{freq}hz.wav"
                self.render_with_effect(
                    jsfx_path=jsfx_path,
                    input_wav=input_wav,
                    output_wav=output_wav,
                    slider_values=slider_values,
                    sample_rate=sample_rate
                )
                
                # Measure output level
                output_samples, _, _ = self.analyzer.read_wav(output_wav)
                output_level = self.analyzer.measure_frequency_response(
                    output_samples, sample_rate, freq
                )
                
                # Calculate attenuation
                if input_level > 0:
                    attenuation_db = 20 * np.log10(output_level / input_level)
                else:
                    attenuation_db = -np.inf
                
                results[freq] = {
                    'input_level': input_level,
                    'output_level': output_level,
                    'attenuation_db': attenuation_db
                }
        
        return results


if __name__ == "__main__":
    # Example test
    print("Testing JSFX framework...")
    
    tester = JSFXTester()
    
    # Test low-pass filter at different frequencies
    results = tester.test_frequency_response(
        jsfx_path="~/.config/REAPER/Effects/Croft/LowPassFilter.jsfx",
        test_frequencies=[100, 500, 1000, 2000, 5000],
        slider_values={"frequencySlider": 1000},
        sample_rate=48000
    )
    
    print("\nLow-pass filter @ 1000Hz cutoff:")
    print("-" * 50)
    for freq, data in sorted(results.items()):
        print(f"{freq:5d} Hz: {data['attenuation_db']:+6.2f} dB")
