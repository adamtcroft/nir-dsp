#!/usr/bin/env python3
"""
Signal generator for JSFX testing.
Generates various test signals (impulse, sine, sweep) as WAV files.
"""

import numpy as np
import wave
import struct
from pathlib import Path


class SignalGenerator:
    """Generate test audio signals for JSFX testing."""
    
    def __init__(self, sample_rate=48000, duration=1.0, channels=2):
        """
        Initialize signal generator.
        
        Args:
            sample_rate: Sample rate in Hz (default 48000)
            duration: Duration in seconds (default 1.0)
            channels: Number of channels (default 2 for stereo)
        """
        self.sample_rate = sample_rate
        self.duration = duration
        self.channels = channels
        self.num_samples = int(sample_rate * duration)
        
    def generate_impulse(self, amplitude=0.5):
        """
        Generate an impulse signal (single sample peak).
        Useful for measuring impulse response.
        
        Args:
            amplitude: Peak amplitude (0.0 to 1.0)
            
        Returns:
            numpy array of shape (num_samples, channels)
        """
        signal = np.zeros((self.num_samples, self.channels))
        signal[0, :] = amplitude
        return signal
    
    def generate_sine(self, frequency, amplitude=0.5):
        """
        Generate a sine wave at specified frequency.
        
        Args:
            frequency: Frequency in Hz
            amplitude: Peak amplitude (0.0 to 1.0)
            
        Returns:
            numpy array of shape (num_samples, channels)
        """
        t = np.linspace(0, self.duration, self.num_samples, endpoint=False)
        signal = amplitude * np.sin(2 * np.pi * frequency * t)
        # Duplicate to all channels
        signal = np.tile(signal.reshape(-1, 1), (1, self.channels))
        return signal
    
    def generate_sweep(self, f_start=20, f_end=20000, amplitude=0.5, log_sweep=True):
        """
        Generate a frequency sweep (chirp).
        Useful for measuring frequency response.
        
        Args:
            f_start: Starting frequency in Hz
            f_end: Ending frequency in Hz
            amplitude: Peak amplitude (0.0 to 1.0)
            log_sweep: If True, use logarithmic sweep; if False, linear
            
        Returns:
            numpy array of shape (num_samples, channels)
        """
        t = np.linspace(0, self.duration, self.num_samples, endpoint=False)
        
        if log_sweep:
            # Logarithmic sweep (better for audio analysis)
            k = (f_end / f_start) ** (1 / self.duration)
            phase = 2 * np.pi * f_start * (k ** t - 1) / np.log(k)
        else:
            # Linear sweep
            phase = 2 * np.pi * (f_start * t + (f_end - f_start) * t**2 / (2 * self.duration))
        
        signal = amplitude * np.sin(phase)
        # Duplicate to all channels
        signal = np.tile(signal.reshape(-1, 1), (1, self.channels))
        return signal
    
    def generate_white_noise(self, amplitude=0.1):
        """
        Generate white noise.
        
        Args:
            amplitude: RMS amplitude (0.0 to 1.0)
            
        Returns:
            numpy array of shape (num_samples, channels)
        """
        signal = amplitude * np.random.randn(self.num_samples, self.channels)
        return signal
    
    def save_wav(self, signal, filename):
        """
        Save signal as WAV file.
        
        Args:
            signal: numpy array of shape (num_samples, channels)
            filename: Output filename (can be string or Path)
        """
        filename = Path(filename)
        filename.parent.mkdir(parents=True, exist_ok=True)
        
        # Ensure signal is in range [-1, 1]
        signal = np.clip(signal, -1.0, 1.0)
        
        # Convert to 16-bit PCM
        signal_int = (signal * 32767).astype(np.int16)
        
        with wave.open(str(filename), 'w') as wav_file:
            wav_file.setnchannels(self.channels)
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            
            # Interleave channels
            for frame in signal_int:
                for sample in frame:
                    wav_file.writeframes(struct.pack('<h', sample))


def generate_standard_test_signals(output_dir="test_signals", sample_rate=48000):
    """
    Generate a standard set of test signals.
    
    Args:
        output_dir: Directory to save test signals
        sample_rate: Sample rate in Hz
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating test signals in {output_path}")
    
    # Impulse
    gen = SignalGenerator(sample_rate=sample_rate, duration=1.0)
    impulse = gen.generate_impulse(amplitude=0.8)
    gen.save_wav(impulse, output_path / "impulse.wav")
    print("  ✓ impulse.wav")
    
    # Sine waves at various frequencies
    for freq in [100, 440, 1000, 5000, 10000]:
        gen = SignalGenerator(sample_rate=sample_rate, duration=2.0)
        sine = gen.generate_sine(freq, amplitude=0.5)
        gen.save_wav(sine, output_path / f"sine_{freq}hz.wav")
        print(f"  ✓ sine_{freq}hz.wav")
    
    # Frequency sweep
    gen = SignalGenerator(sample_rate=sample_rate, duration=5.0)
    sweep = gen.generate_sweep(f_start=20, f_end=20000, amplitude=0.3)
    gen.save_wav(sweep, output_path / "sweep_20_20k.wav")
    print("  ✓ sweep_20_20k.wav")
    
    # White noise
    gen = SignalGenerator(sample_rate=sample_rate, duration=3.0)
    noise = gen.generate_white_noise(amplitude=0.1)
    gen.save_wav(noise, output_path / "white_noise.wav")
    print("  ✓ white_noise.wav")
    
    print("Test signal generation complete!")


if __name__ == "__main__":
    generate_standard_test_signals()
