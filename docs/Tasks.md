1. Convert your python scripts to Lua where possible and remove the python work
    - If this is not possible or somehow "less good" communicate that to me in 
      our communications file
2. Modify the Low Pass filter to work on all channel configurations from a mono 
   source up to a 7.1 source.  It should auto-detect how many channels there are 
   and process appropriately.  It should not process any additional channels 
   that are unnecessary to reduce CPU usage.
   - As a sub-task, change the name from "Biquad Low Pass Filter (NIR)" to "Low 
     Pass Filter (NIR)"
2. Please create a High Pass Filter in the exact same style as our existing Low 
   Pass Filter
