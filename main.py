import cv2 as cv
import numpy as np
import pyautogui as ui
import time
from windowcapture import WindowCapture
from vision import Vision


def main():
    # inicializa WindowCapture class
    wincap = WindowCapture('RuneLite - xCloudd')
    # Inicializa Vision class
    Vision_barbfishing = Vision('barbfish.jpg')

    Vision_barbfishing.init_control_gui()

    loop_time = time.time()
    while(True):

        # Get the image
        screenshot = wincap.get_screenshot()

        # pre-process the image
        processed_image = Vision_barbfishing.apply_hsv_filter(screenshot)

        # Do object detection
        rectangles = Vision_barbfishing.find(processed_image, 0.5)

        # Draw the detection results onto the original image
        output_image = Vision_barbfishing.draw_rectangles(screenshot, rectangles)

        # display the processed image
        cv.imshow('Matches', output_image)

        # Debug Loop rate
        print('FPS {}'.format(1 / (time.time() - loop_time)))
        loop_time = time.time()


        #press 'q' to quit
        if cv.waitKey(1) == ord('q'):
            cv.destroyAllWindows()
            break

    print('Done.')


main()
