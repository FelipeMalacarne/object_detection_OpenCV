import cv2 as cv
import numpy as np
import pyautogui as ui
import time
from windowcapture import WindowCapture
from vision import Vision
from threading import Thread
from detection import Detection
from bot import FishingBot, BotState

# This function will be performed inside another thread
def bot_actions(rectangles):
    # Take bot Actions
    if len(rectangles) > 0:
        targets = vision.get_click_points(rectangles)
        target = wincap.get_screen_position(targets[0])
        ui.moveTo(x=target[0], y=target[1])
        ui.click()
        time.sleep(5)
    # let the main loop know when this process is completed
    global is_bot_in_action
    is_bot_in_action = False

DEBUG = True


# inicializa WindowCapture class
wincap = WindowCapture('RuneLite - xCloudd')
# load the detector
detector = Detection('./fishing_images/barbfish.jpg')
# load empty Vision Class
vision = Vision()
# initialize the bot
bot = FishingBot((wincap.offset_x, wincap.offset_y), (wincap.w, wincap.h))

# this variable is used to notify the main loop when the bot actions have completed
is_bot_in_action = False

wincap.start()
detector.start()
bot.start()

loop_time = time.time()

while(True):

    # if we do not have a screenshot yet, dont run the code below
    if wincap.screenshot is None:
        continue

    # Give the current screenshot to detector to search objects
    detector.update(wincap.screenshot)

    # update the bot with the data
    if bot.state == BotState.INITIALIZING:
        # while bot is waiting to start, give some targets to work on
        targets = vision.get_click_points(detector.rectangles)
        bot.update_targets(targets)

    elif bot.state == BotState.SEARCHING:
        # when searching, bot needs know the click points and an updated screenshot to verify the hover tooltip once it has moved the mouse to that position
        targets = vision.get_click_points(detector.rectangles)
        bot.update_targets(targets)
        bot.update_screenshot(wincap.screenshot)

    elif bot.state == BotState.MOVING:
        # when moving we need fresh screenshots to determine when we have stopped moving
        bot.update_screenshot(wincap.screenshot)

    elif bot.state == BotState.FISHING:
        # when fishing we need fresh screenshots to see if inventory is full
        bot.update_screenshot(wincap.screenshot)

    




    if DEBUG:
        # Draw the detection results onto the original image
        detection_image = vision.draw_rectangles(wincap.screenshot, detector.rectangles)
        # display the processed image
        cv.imshow('Matches', detection_image)

    # Take bot actions
    # separate threads
    # if not is_bot_in_action:
    #     is_bot_in_action = True
    #     t = Thread(target=bot_actions, args=(detector.rectangles,))
    #     t.start()

       

    # Debug Loop rate
    # print('FPS {}'.format(1 / (time.time() - loop_time)))
    # loop_time = time.time()


    #press 'q' to quit
    if cv.waitKey(1) == ord('q'):
        wincap.stop()
        detector.stop()
        bot.stop()
        cv.destroyAllWindows()
        break

print('Done.')
