1. Write a biquad-based low-pass filter in JSFX
    - Build using proper biquad filter (not simple exponential smoothing)
    - Reference: existing filter in ~/.config/REAPER/Effects/Croft/LowPassFilter.jsfx
    - Improvements needed:
        * Better UI layout
        * Logarithmic frequency fader (more detail in low frequencies)
        * Better fader throw/response
        * Keep same parameter set (frequency, resonance if applicable)
    - Test with new testing framework in /testing/
