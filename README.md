# inky_frame
picture frame with inky_frame
Consists of a modified main.py and a dedicated picture_frame.py.

# How to operate
You can put several folders in the base directory of your SD-Card, each containig several pictures in jpg-format. Best, if you converted the jpg to the correct screen resolution
* paste code for mass transformation using imagemagic
After startup and selection of the picture_frame in main.py, the system selects the first (alphabetical order) folder and displays a random image out of that folder.
* Press and hold Button "A" until LED-A starts to light. Release A. picture_frame will select the next folder in alphabetical order and display a random picture of that folder
* Press and hold Button "B" until LED-B starts to light. Release B. picture frame will display another random picture of the currently used folder
* After updateting the picture inky_frame will wait for 120 minutes and update the picture with another randomly selected picture within the currently used folder (same as "press button B")

# Know Bugs
* Inky_Frame regularly freezes during update process of picture in battery-operated mode. Indication is both LED-D and LED-E are light. picture_frame converts JPG to a usable grafics format for inky_frame. LED-E turns off, LED-D stays on. The command is given to update the picture. Here nothing happens, indefinatelly.
* Connecting Inky_Frame via USB and Thonny, strange error messages of "time.sleep(0.5)" in line 18 of main.py does not exist. Can only be remedied by importing time in command line mode and starting main.py by hand. A machine.reset() will most often trigger this error again.
