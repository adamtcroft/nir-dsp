#!/usr/bin/env python3
"""
Example test script for LowPassFilter.jsfx
Demonstrates how to use the JSFX testing framework.
"""

import sys
from pathlib import Path

# Add testing directory to path
sys.path.insert(0, str(Path(__file__).parent))

from jsfx_tester import JSFXTester
from signal_generator import generate_standard_test_signals


def test_lowpass_filter():
    """Test the low-pass filter at various cutoff frequencies."""
    
    print("=" * 60)
    print("JSFX Low-Pass Filter Test")
    print("=" * 60)
    
    # Initialize tester
    tester = JSFXTester()
    jsfx_path = str(Path.home() / ".config/REAPER/Effects/Croft/LowPassFilter.jsfx")
    
    # Test frequencies
    test_freqs = [50, 100, 200, 500, 1000, 2000, 5000, 10000]
    
    # Test at different cutoff frequencies
    cutoff_frequencies = [100, 500, 1000, 2000]
    
    for cutoff in cutoff_frequencies:
        print(f"\n{'=' * 60}")
        print(f"Testing with cutoff frequency: {cutoff} Hz")
        print(f"{'=' * 60}")
        print(f"{'Frequency':>10} | {'Attenuation':>12} | {'Status':>10}")
        print("-" * 60)
        
        results = tester.test_frequency_response(
            jsfx_path=jsfx_path,
            test_frequencies=test_freqs,
            slider_values={"frequencySlider": cutoff},
            sample_rate=48000
        )
        
        for freq in sorted(results.keys()):
            data = results[freq]
            atten_db = data['attenuation_db']
            
            # Determine status
            if freq < cutoff * 0.5:
                # Should pass with minimal attenuation
                status = "PASS" if atten_db > -3 else "FAIL"
            elif freq > cutoff * 2:
                # Should be significantly attenuated
                status = "PASS" if atten_db < -6 else "FAIL"
            else:
                # Transition region
                status = "OK"
            
            print(f"{freq:>10} Hz | {atten_db:>+10.2f} dB | {status:>10}")
        
        # Summary
        passband_freqs = [f for f in test_freqs if f < cutoff * 0.5]
        stopband_freqs = [f for f in test_freqs if f > cutoff * 2]
        
        if passband_freqs:
            avg_passband = sum(results[f]['attenuation_db'] for f in passband_freqs) / len(passband_freqs)
            print(f"\nAverage passband attenuation: {avg_passband:+.2f} dB")
        
        if stopband_freqs:
            avg_stopband = sum(results[f]['attenuation_db'] for f in stopband_freqs) / len(stopband_freqs)
            print(f"Average stopband attenuation: {avg_stopband:+.2f} dB")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_lowpass_filter()
