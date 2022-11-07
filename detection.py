import cv2 as cv
from threading import Thread, Lock
from vision import Vision
import numpy as np

class Detection:

    # Threading properties
    stopped = True
    lock = None
    rectangles = []
    # properties
    screenshot = None
    needle_img = None
    needle_w = 0
    needle_h = 0
    method = None



    def __init__(self, needle_img_path,method=cv.TM_CCOEFF_NORMED):
        # Create a thread lokc object
        self.lock = Lock()
        self.needle_img = cv.imread(needle_img_path, cv.IMREAD_UNCHANGED)

        #Save the dimensions of the needle_img
        self.needle_w = self.needle_img.shape[1]
        self.needle_h = self.needle_img.shape[0]

        # 6 metodos
        # TM_CCOEFF_NORMED, TM_CCOEFF, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF NORMED
        self.method = method

    def update(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True
    
    def run(self):
        while not self.stopped:
            if not self.screenshot is None:
                # do object detection
                rectangles = self.find(self.screenshot, 0.5)
                # lock the thread while updating the results
                self.lock.acquire()
                self.rectangles = rectangles
                self.lock.release()



    def find(self, haystack_img, threshold=0.5, max_results=10):
        # Run OpenCV Algorithm
        result = cv.matchTemplate(haystack_img, self.needle_img, self.method)

        locations = np.where(result >= threshold)
        locations = list(zip(*locations[::-1]))

        if not locations:
            return np.array([], dtype=np.int32).reshape(0, 4)

        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), self.needle_w, self.needle_h]
            rectangles.append(rect)
            rectangles.append(rect)

        rectangles, weights = cv.groupRectangles(rectangles, 1, 0.05)

        # For performance, return a limited number of results
        if len(rectangles) > max_results:
            print('warning: too many results, raise the threshold')
            rectangles = rectangles[:max_results]

        return rectangles   