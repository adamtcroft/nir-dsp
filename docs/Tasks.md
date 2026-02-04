1. Convert your python scripts to Lua where possible and remove the python work
    - If this is not possible or somehow "less good" communicate that to me in 
      our communications file
2. Modify the Low Pass filter to work on all channel configurations from a mono 
   source up to a 7.1 source.  It should auto-detect how many channels there are 
   and process appropriately.  It should not process any additional channels 
   that are unnecessary to reduce CPU usage.
3. Change the Q slider on both the low pass filter and the high pass filter to 
   have a logarithmic response like the frequency slider.  Choose a center value 
   for the slider that makes sense in a logarithmic throw.  Currently, the 
       slider seems much more sensitive on the left (lower) end than the right 
       (higher)
