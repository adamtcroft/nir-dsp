# Rules.md

## Languages
We are currently developing JSFX effects in EEL2
If you create any tools or helper scripts or anything for REAPER, favor Lua over 
Python
If you've already written anything in Python, please convert it to Lua

## Actions
If there are any style guides in this folder per-language, please reference them 
before working.

If you learn anything from the development process while working, please write 
it in this file.

## Tools
We are using REAPER to develop and test audio effects.  You can run that using 
the command "reaper" from CLI.

## Build Steps
Anything you build needs to be saved in this repository and cloned to 
~/.config/REAPER/Effects/Croft to be tested

## Communication
You are often run overnight from a cron job.  If you have anything to 
communicate, summarize, or express to me, please write in "docs/Communication.md" 
so I can check it later.  If you ever see another "Communication.md" file, 
consolidate it with the one in docs.  New entries should always go at the top of 
the file.

## Testing
All of your work and effects need to be tested and verified using your testing 
suite for objective measurements.  If your testing suite is ineffective, not 
enough coverage, or inconclusive, do your best to expand it appropriately.

## Packages
Err on the side of not downloading packages from the internet when creating 
scripts (ie: numpy).  I do not have a way to verify that packages you may find 
are safe.  I also don't want you to go make a massive library for yourself - but 
building small code to test things is okay.
