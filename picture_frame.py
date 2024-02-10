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
debug_level = 3

inky_frame.pcf_to_pico_rtc()

# set up the display
graphics = PicoGraphics(DISPLAY)
WIDTH, HEIGHT = graphics.get_bounds()
graphics.set_font("bitmap8")


new_folder=False
new_picture=False
if ih.inky_frame.button_a.read():
    if debug_level > 1:
        ih.inky_frame.button_a.led_on()
        print("Button A was pressed, thus trying to find new folder")
    new_folder=True
    new_picture=True

if ih.inky_frame.button_b.read():
    if debug_level > 1:
        ih.inky_frame.button_b.led_on()
        print("Button B was pressed or rtc-event happend, thus trying to display new picture")
        time.sleep(1)
    new_picture=True
    
if ih.inky_frame.button_c.read():
    ih.inky_frame.button_c.led_on()
    time.sleep(1)
    ih.inky_frame.button_c.led_off()
    time.sleep(1)
    ih.inky_frame.button_c.led_on()
    time.sleep(1)
    ih.state['file_order_random']= not ih.state['file_order_random']
    ih.save_state=(ih.state)
    ih.inky_frame.button_c.led_off()
    if ih.state['file_order_random']:
        ih.inky_frame.button_c.led_on()
        time.sleep(0.2)
        ih.inky_frame.button_c.led_off()
        time.sleep(0.5)
        ih.inky_frame.button_c.led_on()
        time.sleep(0.2)
        ih.inky_frame.button_c.led_off()
    else:
        ih.inky_frame.button_c.led_on()
        time.sleep(0.5)
        ih.inky_frame.button_c.led_off()
        time.sleep(0.2)
        ih.inky_frame.button_c.led_on()
        time.sleep(0.5)
        ih.inky_frame.button_c.led_off()
    
if inky_frame.woken_by_rtc():
    if debug_level > 1:
        ih.inky_frame.button_c.led_on()
        print("Button B was pressed or rtc-event happend, thus trying to display new picture")
    new_picture=True
    
# set up the SD card
try:
    sd_spi = SPI(0, sck=Pin(18, Pin.OUT), mosi=Pin(19, Pin.OUT), miso=Pin(16, Pin.OUT))
    sd = sdcard.SDCard(sd_spi, Pin(22))
    os.mount(sd, "/sd")
except:
    ih.inky_frame.button_d.led_on()
    ih.inky_frame.button_e.led_on()
    print("SD card could not be read")
    time.sleep(5)
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
        if debug_level > 2:
            print("in first if for \"index_searched\"")
        for i in range(len(subfolders)):
            if debug_level > 2:
                print("in loop: " + str(i) + " with " + subfolders[i])
            if not index_searched:
                if debug_level > 2:
                    print("before if")
                if subfolders[i]==pic_cur_subfolder:
                    if debug_level > 2:
                        print("in if")
                    index_searched=i
        if index_searched != None:
            if debug_level > 2:
                print("index found is: "+str(index_searched)+" and used is "+str((index_searched+1)%len(subfolders)))
            picture_current_subfolder=subfolders[(index_searched+1)%len(subfolders)]
        else:
            picture_current_subfolder=subfolders[0]
    else:
        picture_current_subfolder=subfolders[0]
    pictures_full_path = pic_folder + "/" + picture_current_subfolder
    if debug_level > 0:
        print("Current subfolder used: "+pic_folder+"/"+picture_current_subfolder)
    ih.state['current_subfolder'] = picture_current_subfolder
    ih.save_state(ih.state)
    return picture_current_subfolder

def get_new_picture_filename(full_path):
    files = os.listdir(full_path)
    # remove files from the list that aren't .jpgs or .jpegs
    files = [f for f in files if f.endswith(".jpg") or f.endswith(".jpeg")]
    if ih.state['file_order_random']:
        if debug_level > 2:
            print("Selecting new random picture")
        file = files[random.randrange(len(files))-1]
    else:
        if debug_level > 2:
            print("Selecting new ordered picture")
        picture_index=ih.state['picture_index']
        picture_index += 1
        if len(files)<= picture_index:
            picture_index=0
        file = files[picture_index]
        ih.state['picture_index']=picture_index
    ih.state['update_picture'] = False
    ih.save_state(ih.state)
    return file

def display_image(filename):

    # Open the JPEG file
    ih.inky_frame.button_e.led_on()
    j.open_file(filename)
    
    # Decode the JPEG
    j.decode(0, 0, jpegdec.JPEG_SCALE_FULL)
    ih.inky_frame.button_e.led_off()

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
    new_picture=ih.state['update_picture'] or new_picture
    if debug_level > 1:
        print("Set new_picture to: "+str(new_picture))
except:
    new_picture=True
    print("Set new_picture in exception to: "+str(new_picture))

try:
    picture_current_subfolder=ih.state['current_subfolder']
    if not is_dir(picture_folder+"/"+picture_current_subfolder):
        new_folder=True
        print("Found subfolder in state, but subfolder does not exist")
    print("Current subfolder set to: "+picture_current_subfolder)
except:
    new_folder=True
    print("Current subfolder not set")
    
gc.collect()


while True:
    # pick a random file
    inky_frame.led_busy.brightness(1)
    inky_frame.led_busy.on()
    
    #if ih.inky_frame.button_a.read():
    #    ih.inky_frame.button_a.led_on()
    #    new_folder=True
    #    new_picture=True
    #    gc.collect()
    #    time.sleep(.5)
    #    machine.reset()
        
    #if ih.inky_frame.button_b.read():
    #    ih.inky_frame.button_b.led_on()
    #    time.sleep(.5)
    #    new_picture=True
    #    machine.reset()
        
    if new_folder:
        picture_current_subfolder=take_next_folder(picture_folder, picture_current_subfolder)
        gc.collect()
    
    pictures_full_path = picture_folder + "/" + picture_current_subfolder
    
    if new_picture:
        ih.clear_button_leds()
        ih.inky_frame.button_d.led_on()
        file=get_new_picture_filename(pictures_full_path)
        gc.collect()
        # Open the file
        print(f"Displaying {pictures_full_path}/{file}")
        display_image(pictures_full_path + "/" + file)
        print("Done drawing")
    
    ih.clear_button_leds()
    inky_frame.led_busy.off()
    
    new_picture=False
    new_folder=False

    # Sleep or wait for a bit
    gc.collect()
    print(f"Sleeping for {UPDATE_INTERVAL} minutes")
    inky_frame.sleep_for(UPDATE_INTERVAL)
    new_picture=True
