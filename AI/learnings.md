# AI Learnings - JSFX Testing Framework

## Session: 2026-02-05

### Task: Python to Lua Conversion

#### Key Learnings

1. **Not all Python code should be converted to Lua**
   - Python's numpy library provides essential signal processing capabilities (FFT, array operations)
   - Lua has no standard FFT library, making audio analysis very difficult
   - Pure Lua implementation of numpy features would be slow and error-prone

2. **Partial conversion is sometimes the right answer**
   - `reaper_project.py` was purely string manipulation - easy to port
   - `signal_generator.py` and `jsfx_tester.py` rely heavily on numpy - not practical to port
   - Created Lua version of reaper_project while keeping Python version for compatibility

3. **Interdependencies matter**
   - The testing framework has imports between modules
   - Can't just delete Python files without breaking the import chain
   - `jsfx_tester.py` imports from `reaper_project.py` and `signal_generator.py`

4. **Alternative approaches exist**
   - REAPER's JS effects have built-in FFT functions
   - ReaScript could potentially provide Lua-based audio analysis using REAPER internals
   - But this would be a complete rewrite, not a simple port

#### Technical Notes

**Lua module pattern used:**
```lua
local Module = {}
Module.__index = Module

function Module.new()
    local self = setmetatable({}, Module)
    return self
end

return Module
```

**Lua path handling:**
```lua
-- Extract filename from path
local name = path:match("([^/\\]+)$")

-- Get absolute path using shell
local handle = io.popen("pwd")
local cwd = handle:read("*a"):gsub("%s+$", "")
handle:close()
```

---

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

## Session: 2026-01-31 (Biquad Filter)

### Task Completed
Created a proper biquad-based low-pass filter to replace the exponential smoothing approach.

### Key Learnings

#### Biquad Filter Math
A biquad (bi-quadratic) filter is a second-order IIR filter. The difference equation:
```
y[n] = b0*x[n] + b1*x[n-1] + b2*x[n-2] - a1*y[n-1] - a2*y[n-2]
```

For a lowpass filter using RBJ (Robert Bristow-Johnson) cookbook formulas:
```
omega = 2*π*f/fs
alpha = sin(omega) / (2*Q)
a0 = 1 + alpha

b0 = ((1 - cos(omega)) / 2) / a0
b1 = (1 - cos(omega)) / a0
b2 = ((1 - cos(omega)) / 2) / a0
a1 = (-2 * cos(omega)) / a0
a2 = (1 - alpha) / a0
```

Key characteristics:
- 2-pole filter: -12 dB/octave rolloff
- Q controls resonance at cutoff (0.707 = Butterworth, maximally flat)
- Much sharper rolloff than 1-pole exponential smoothing

#### EEL2 Object-Oriented Pattern
JSFX/EEL2 supports a pseudo-OOP pattern using namespaces:
```
function biquad_init()
(
    this.x1 = 0;  // 'this' refers to the namespace
    this.x2 = 0;
    ...
);

// Usage:
filterL.biquad_init();  // filterL is the namespace
output = filterL.biquad_process(input);
```

This allows multiple filter instances without manual state management.

#### Logarithmic Frequency Mapping
Audio frequencies are perceived logarithmically. For better UI control:
```
freq = exp(log(minFreq) + (slider/100) * (log(maxFreq) - log(minFreq)))
```

This gives more resolution in low frequencies where the ear is more sensitive.
For 20Hz-20kHz range:
- 50% slider ≈ 632 Hz (geometric center)
- Linear would give 10,010 Hz at 50%

#### JSFX Slider Scaling Modifiers
JSFX supports built-in slider scaling through special syntax modifiers in the slider declaration:

**`:log=X` modifier** - Logarithmic scaling where X is the midpoint:
```
slider1:cutoffFreq=632<20,20000,1:log=632>Cutoff Frequency (Hz)
```
- The `:log=X` parameter creates a logarithmic slider scale
- `X` specifies the value at the center (50%) of the slider throw
- For audio frequencies, 632 Hz is ideal as the geometric center of 20Hz-20kHz
- This provides finer control in the bass/low-mid range where it matters most
- Replaces manual logarithmic mapping calculations in code
- Reference: https://www.reaper.fm/sdk/js/js.php

**`:sqr=X` modifier** - Polynomial scaling:
- `X` is the exponent of the polynomial (2 is default for quadratic)
- Less commonly used for audio parameters

**Important note**: Changing the scaling type or the X value can affect existing projects that automate the parameter, as the slider position-to-value mapping changes.

#### Function Definition Order in EEL2
From the EEL2 rule: helper functions must be defined BEFORE they're used in @slider/@block/@sample sections, or imported from .jsfx-inc. The sliderToFrequency() function was correctly placed in @init where it can be called from both @init and @slider.

### Files Created/Modified

1. `/plugins/library.jsfx-inc` - Added biquad filter functions:
   - `biquad_init()` - Initialize filter state
   - `biquad_setLowPass(cutoff, q, sampleRate)` - Calculate coefficients
   - `biquad_process(input)` - Process one sample

2. `/plugins/BiquadLowPass.jsfx` - New effect with:
   - Logarithmic frequency slider (20Hz-20kHz)
   - Q/resonance control (0.1-10, default 0.707)
   - Proper stereo handling with separate filter instances
   - Clean, well-commented code

3. `/testing/test_biquad_lowpass.py` - Test script that:
   - Calculates proper slider values for target frequencies
   - Tests at multiple cutoffs (100, 500, 1K, 2K, 5K Hz)
   - Verifies expected -12dB/octave rolloff
   - Provides comprehensive pass/fail analysis

### Improvements Over Original

**Old LowPassFilter.jsfx:**
- Simple exponential smoothing (1-pole)
- Cascaded 4x for steeper rolloff
- Linear frequency slider (0-500 Hz only)
- Less predictable frequency response

**New BiquadLowPass.jsfx:**
- True biquad filter (2-pole)
- Single stage with adjustable Q
- Logarithmic frequency (20Hz-20kHz full range)
- Precise -12dB/octave rolloff
- Resonance control for different filter characteristics
- Better code organization and documentation

### Testing Limitations

Couldn't run actual tests in sandbox due to missing numpy. Testing will need to happen in main environment where:
- python-numpy package is installed
- REAPER is available and configured
- Full testing framework can execute

The test script is ready and should work when dependencies are met.

### Task Status in docs/Tasks.md

Completed the foundation work for task #1. The biquad filter itself is done, but the task mentions several sub-improvements that could still be addressed:
- ✅ Proper biquad filter (not exponential smoothing)
- ✅ Logarithmic frequency fader
- ✅ Better UI with wider frequency range
- ✅ Resonance/Q parameter
- ⚠️  Testing with framework (script ready, needs numpy)

The core "build a biquad-based low-pass filter" is complete. Further refinements could include UI polish or additional features, but the fundamental work is done.
