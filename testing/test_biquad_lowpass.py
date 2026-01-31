#!/usr/bin/env python3
"""
Test script for BiquadLowPass.jsfx
Tests the new biquad-based low-pass filter with logarithmic frequency control.
"""

import sys
from pathlib import Path

# Add testing directory to path
sys.path.insert(0, str(Path(__file__).parent))

from jsfx_tester import JSFXTester


def test_biquad_lowpass():
    """Test the biquad low-pass filter at various cutoff frequencies."""
    
    print("=" * 60)
    print("JSFX Biquad Low-Pass Filter Test")
    print("=" * 60)
    
    # Initialize tester
    tester = JSFXTester()
    jsfx_path = str(Path.home() / ".config/REAPER/Effects/Croft/BiquadLowPass.jsfx")
    
    # Test frequencies
    test_freqs = [50, 100, 200, 500, 1000, 2000, 5000, 10000]
    
    # Test at different cutoff frequencies
    # freqSlider is 0-100%, logarithmic mapping from 20Hz to 20kHz
    # We'll calculate the slider values for specific frequencies
    def freq_to_slider(freq_hz):
        """Convert frequency to slider percentage (logarithmic)."""
        import math
        min_freq = 20
        max_freq = 20000
        log_min = math.log(min_freq)
        log_max = math.log(max_freq)
        log_freq = math.log(freq_hz)
        return ((log_freq - log_min) / (log_max - log_min)) * 100
    
    # Test frequencies
    test_cutoffs = [100, 500, 1000, 2000, 5000]
    
    for cutoff in test_cutoffs:
        slider_value = freq_to_slider(cutoff)
        print(f"\n{'=' * 60}")
        print(f"Testing with cutoff: {cutoff} Hz (slider: {slider_value:.1f}%)")
        print(f"Resonance Q: 0.707 (Butterworth)")
        print(f"{'=' * 60}")
        print(f"{'Frequency':>10} | {'Attenuation':>12} | {'Status':>10}")
        print("-" * 60)
        
        results = tester.test_frequency_response(
            jsfx_path=jsfx_path,
            test_frequencies=test_freqs,
            slider_values={"freqSlider": slider_value, "qSlider": 0.707},
            sample_rate=48000
        )
        
        for freq in sorted(results.keys()):
            data = results[freq]
            atten_db = data['attenuation_db']
            
            # Determine status based on biquad characteristics
            # Biquad has -12dB/octave rolloff (2-pole filter)
            if freq < cutoff * 0.7:
                # Passband - should be close to 0dB
                status = "PASS" if atten_db > -3 else "FAIL"
            elif freq > cutoff * 1.5:
                # Stopband - should show rolloff
                status = "PASS" if atten_db < -6 else "WARN"
            else:
                # Transition region around -3dB point
                status = "OK"
            
            print(f"{freq:>10} Hz | {atten_db:>+10.2f} dB | {status:>10}")
        
        # Summary statistics
        passband_freqs = [f for f in test_freqs if f < cutoff * 0.7]
        stopband_freqs = [f for f in test_freqs if f > cutoff * 1.5]
        
        if passband_freqs:
            avg_passband = sum(results[f]['attenuation_db'] for f in passband_freqs) / len(passband_freqs)
            print(f"\nAverage passband attenuation: {avg_passband:+.2f} dB")
        
        if stopband_freqs:
            avg_stopband = sum(results[f]['attenuation_db'] for f in stopband_freqs) / len(stopband_freqs)
            print(f"Average stopband attenuation: {avg_stopband:+.2f} dB")
            
            # Calculate approximate rolloff
            if len(stopband_freqs) >= 2:
                freq1 = stopband_freqs[0]
                freq2 = stopband_freqs[-1]
                atten1 = results[freq1]['attenuation_db']
                atten2 = results[freq2]['attenuation_db']
                octaves = math.log2(freq2 / freq1)
                rolloff = (atten2 - atten1) / octaves
                print(f"Measured rolloff: {rolloff:.1f} dB/octave (expected: ~-12 dB/oct)")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    import math
    test_biquad_lowpass()
