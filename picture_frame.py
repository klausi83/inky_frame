"""
An offline image gallery that displays a random image from your SD card
and updates on a timer.

Copy images to the root of your SD card by plugging it into a computer.

If you want to use your own images they must be the screen dimensions
(or smaller) and saved as *non-progressive* jpgs.

Make sure to uncomment the correct size for your display!
"""

# from picographics import PicoGraphics, DISPLAY_INKY_FRAME as DISPLAY    # 5.7"
# from picographics import PicoGraphics, DISPLAY_INKY_FRAME_4 as DISPLAY  # 4.0"
from picographics import PicoGraphics, DISPLAY_INKY_FRAME_7 as DISPLAY  # 7.3"
from machine import Pin, SPI
import gc
import time
import jpegdec
import sdcard
import os
import inky_frame
import inky_helper as ih
import random

# how often to change image (in minutes)
UPDATE_INTERVAL = 120

inky_frame.pcf_to_pico_rtc()

# set up the display
graphics = PicoGraphics(DISPLAY)

new_folder=False
new_picture=True
if ih.inky_frame.button_a.read():
    ih.inky_frame.button_a.led_on()
    new_folder=True
    new_picture=True
    print("Button A was pressed, thus trying to find new folder")
if ih.inky_frame.button_b.read() or inky_frame.woken_by_rtc():
    ih.inky_frame.button_b.led_on()
    new_picture=True
    print("Button B was pressed or rtc-event happend, thus trying to display new picture")

# set up the SD card
try:
    sd_spi = SPI(0, sck=Pin(18, Pin.OUT), mosi=Pin(19, Pin.OUT), miso=Pin(16, Pin.OUT))
    sd = sdcard.SDCard(sd_spi, Pin(22))
    os.mount(sd, "/sd")
except:
    ih.inky_frame.button_d.led_on()
    ih.inky_frame.button_e.led_on()
    print("SD card could not be read")
    time.sleep(3)
    machine.reset()

# Create a new JPEG decoder for our PicoGraphics
j = jpegdec.JPEG(graphics)


def is_dir(path):
    try:
        os.chdir(path)
        os.chdir('/')
        return True
    except:
        return False

def take_next_folder(pic_folder, pic_cur_subfolder=None):
    global picture_current_subfolder
    global pictures_full_path
    global new_picture
    new_picture=True
    subfolders = [ f for f in os.listdir(pic_folder) if is_dir(pic_folder+"/"+f) ]
    print(subfolders)
    subfolders.sort()
    if pic_cur_subfolder:
        index_searched=None
        print("in first if for \"index_searched\"")
        for i in range(len(subfolders)):
            print("in loop: " + str(i) + " with " + subfolders[i])
            if not index_searched:
                print("before if")
                if subfolders[i]==pic_cur_subfolder:
                    print("in if")
                    index_searched=i
        if index_searched != None:
            print("index found is: "+str(index_searched)+" and used is "+str((index_searched+1)%len(subfolders)))
            picture_current_subfolder=subfolders[(index_searched+1)%len(subfolders)]
        else:
            picture_current_subfolder=subfolders[0]
    else:
        picture_current_subfolder=subfolders[0]
    pictures_full_path = pic_folder + "/" + picture_current_subfolder
    print("Current subfolder used: "+pic_folder+"/"+picture_current_subfolder)
    ih.state['current_subfolder'] = picture_current_subfolder
    ih.save_state(ih.state)
    return picture_current_subfolder

def get_new_picture_filename(full_path):
    files = os.listdir(full_path)
    # remove files from the list that aren't .jpgs or .jpegs
    files = [f for f in files if f.endswith(".jpg") or f.endswith(".jpeg")]
    file = files[random.randrange(len(files))]
    return file

def display_image(filename):

    # Open the JPEG file
    j.open_file(filename)

    # Decode the JPEG
    j.decode(0, 0, jpegdec.JPEG_SCALE_FULL)

    # Display the result
    graphics.update()


inky_frame.led_busy.on()
if ih.file_exists("state.json"):
    # Loads the JSON and launches the app
    ih.load_state()

# Get a list of files that are in the directory
picture_folder = "/sd/Bilder"
picture_current_subfolder=None
try:
    picture_current_subfolder=ih.state['current_subfolder']
    if not is_dir(picture_folder+"/"+picture_current_subfolder):
        new_folder=True
        print("Found subfolder in state, but subfolder does not exist")
    print("Current subfolder set to: "+picture_current_subfolder)
except:
    new_folder=True
    print("Current subfolder not set")
    



while True:
    # pick a random file
    inky_frame.led_busy.brightness(1)
    inky_frame.led_busy.on()
    
    pictures_full_path = picture_folder + "/" + picture_current_subfolder
    
    if ih.inky_frame.button_a.read():
        ih.inky_frame.button_a.led_on()
        new_folder=True
        new_picture=True
        gc.collect()
        time.sleep(.5)
        machine.reset()
        
    if ih.inky_frame.button_b.read():
        ih.inky_frame.button_b.led_on()
        time.sleep(.5)
        new_picture=True
        machine.reset()
        
    if new_folder:
        picture_current_subfolder=take_next_folder(picture_folder, picture_current_subfolder)
        gc.collect()
        
    if new_picture:
        file=get_new_picture_filename(pictures_full_path)
        # Open the file
        print(f"Displaying {pictures_full_path}/{file}")
        display_image(pictures_full_path + "/" + file)
    ih.clear_button_leds()
    inky_frame.led_busy.off()
    
    new_picture=False
    new_folder=False

    # Sleep or wait for a bit
    print(f"Sleeping for {UPDATE_INTERVAL} minutes")
    inky_frame.sleep_for(UPDATE_INTERVAL)
