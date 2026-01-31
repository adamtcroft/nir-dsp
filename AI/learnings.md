# AI Learnings - JSFX Testing Framework

## Session: 2026-01-31

### Task Completed
Built a complete automated testing framework for JSFX effects.

### Key Learnings

#### 1. REAPER Command-Line Rendering
- REAPER supports headless rendering via `-renderproject` flag
- Can be fully automated without GUI interaction
- Requires proper .rpp project file structure
- Renders to the project directory, not a specified output path
- Important flags: `-nosplash`, `-close:nosave:exit` for automation

#### 2. REAPER Project File (.rpp) Structure
- Plain text format, relatively simple to generate programmatically
- Key components for testing:
  - SAMPLERATE, TEMPO settings
  - TRACK blocks with FXCHAIN
  - JS effect syntax: `<JS name "path">`
  - Slider values as space-separated numbers after slider count
  - ITEM blocks for media files with absolute paths
  - RENDER_* settings control output format

#### 3. Testing Audio Effects Without Hearing
Since I cannot hear audio, objective measurements are essential:
- **FFT analysis** for frequency response (most useful for filters)
- **RMS measurements** for gain/compression effects
- **Peak measurements** for limiting/clipping detection
- **Windowing** (Hanning) reduces spectral leakage in FFT
- Test at multiple frequencies to map full response curve

#### 4. Python Audio Processing
- `wave` module (stdlib) works but is low-level
- Manual frame-by-frame writing for multi-channel
- NumPy essential for signal processing
- Sample format conversions: int16 → float32 [-1, 1] range
- FFT normalization requires window compensation

#### 5. Test Signal Design
- **Impulses**: Best for impulse response, simplest
- **Sine waves**: Best for frequency response at specific points
- **Sweeps**: Good for full spectrum analysis (logarithmic preferred for audio)
- **White noise**: General testing but harder to analyze
- Duration matters: need enough samples for FFT resolution

#### 6. Development Practices
- Built modular components (generator, project builder, tester, analyzer)
- Each module can be used independently or combined
- Example tests are crucial for demonstrating usage
- Comprehensive documentation reduces future confusion

### Technical Challenges Solved

1. **REAPER output location**: Used glob to find rendered files in temp directory
2. **Slider values**: Must use JSFX variable names, not display names
3. **Multi-channel handling**: Simplified to duplicate mono signals
4. **FFT frequency bins**: Find closest bin to target frequency
5. **Temporary file management**: Used tempfile module for cleanup

### Future Improvements Identified

Things that could enhance the framework:
- Phase response measurement (currently only magnitude)
- Visual plotting (matplotlib for frequency response curves)
- Batch testing multiple effects
- THD (Total Harmonic Distortion) analysis
- Support for non-slider parameters (enums, checkboxes)
- Better error messages when REAPER fails
- Caching of rendered results for faster re-testing

### Math Notes

**Exponential smoothing coefficient** (from existing LowPassFilter):
```
coefficient = 1 - exp(-2 * π * cutoff / sampleRate)
```

This is a 1-pole lowpass filter. The existing filter cascades 4 of these.

**FFT amplitude normalization**:
```
amplitude = |FFT[freq_bin]| / (N / 2)
```
Where N is FFT size. Hanning window adds additional factor.

**dB conversion**:
```
dB = 20 * log10(linear)
linear = 10^(dB/20)
```

### Files Created

1. `/testing/signal_generator.py` - Test signal generation
2. `/testing/reaper_project.py` - .rpp file generation
3. `/testing/jsfx_tester.py` - Main testing framework
4. `/testing/test_lowpass_example.py` - Example test
5. `/testing/README.md` - Documentation

### Testing Status

Framework is complete but untested in practice. The example test script should work but may need debugging when first run with actual REAPER instance.

Potential issues to watch for:
- REAPER path/availability
- Slider name mismatches
- Render output file naming/location
- Timeout issues on slower systems
