1. Convert your python scripts to Lua where possible and remove the python work
    - If this is not possible or somehow "less good" communicate that to me in 
      our communications file
2. Update controls on the Biquad Low Pass filter
    - The low pass filter you made sounds much better than my previous attempt, 
      thank you.  The one you made is now missing controls that I want.
    - First, make an copy of the current low pass filter under "dsp/archive"
    - Second, make the changes below to the current low pass filter under the 
      "dsp" folder (not the archive one you just made).  DON'T make a new plugin 
      altogether, work off of what you already made.
    - Convert the cutoff frequency slider to an actual frequency number, but 
      keep the current slider response range if possible (if not, tell me why in 
      our communications file)
    - Keep the Resonance slider as it is
    - Add a dB/Octave slider like I had in the original so that is adjustable by 
      the user.  It should follow the db/Octave options that the original had.  
      Feel free to modify the underlying DSP math to make it really great if 
      necessary
