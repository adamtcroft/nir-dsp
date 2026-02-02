1. Convert your python scripts to Lua where possible and remove the python work
    - If this is not possible or somehow "less good" communicate that to me in 
      our communications file
    - As a subtask - notice that you have two "Communication.md" files in this 
      repo.  Please consolidate them into a single "Communication.md" file
    - As a subtask - I made changes to your Low Pass Filter on line 10 by adding 
      :log=632.  Please reference https://www.reaper.fm/sdk/js/js.php and update 
      your learnings file with new information.  This change allowed the slider 
      throw to change so that 632hz is the center of the slider, allowing for a 
      logarithmic throw and a more usable slider.
2. Modify the Low Pass filter to work on all channel configurations from a mono 
   source up to a 7.1 source.  It should auto-detect how many channels there are 
   and process appropriately.  It should not process any additional channels 
   that are unnecessary to reduce CPU usage.
   - As a sub-task, change the name from "Biquad Low Pass Filter (NIR)" to "Low 
     Pass Filter (NIR)"
2. Please create a High Pass Filter in the exact same style as our existing Low 
   Pass Filter
