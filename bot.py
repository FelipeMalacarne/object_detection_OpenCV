import cv2 as cv
import pyautogui
from time import sleep, time
from threading import Thread, Lock
from math import sqrt

class BotState:
    INITIALIZING = 0
    SEARCHING = 1
    MOVING = 2
    FISHING = 3
    DROPPING = 4

class FishingBot:

    # constants
    INITIALIZING_SECONDS = 5
    FISHING_SECONDS = 15
    MOVEMENT_STOPPED_THRESHOLD = 0.975
    TOOLTIP_MATCH_THRESHOLD = 0.76
    INVENTORY_MATCH_THRESHOLD = 0.76
    NOT_FISHING_THRESHOLD = 0.65

    # threading properties
    stopped = True
    lock = None

    # properties
    state = None
    targets = []
    screenshot = None
    timestamp = None
    movement_screenshot = None
    window_offset = (0, 0)
    window_w = 0
    window_h = 0
    use_rod_tooltip = None
    full_inventory_message = None
    not_fishing_message = None

    # Constructor 
    def __init__(self, window_offset, window_size):
        # create a thread lock object
        self.lock = Lock()

        self.window_offset = window_offset
        self.window_w = window_size[0]
        self.window_h = window_size[1]

        # pre-load the needle to confirm fishing spot
        self.use_rod_tooltip = cv.imread('./fishing_images/use_rod_tooltip.jpg', cv.IMREAD_UNCHANGED) 
        self.full_inventory_message = cv.imread('./fishing_images/full_inventory.jpg', cv.IMREAD_UNCHANGED)
        self.not_fishing_message = cv.imread('./fishing_images/not_fishing.jpg', cv.IMREAD_UNCHANGED)

        # start bot in the initializing mode to allow mark the time which started
        self.state = BotState.INITIALIZING
        self.timestamp = time()

    # threading methods
    def update_targets(self, targets):
        self.lock.acquire()
        self.targets = targets
        self.lock.release()

    def update_screenshot(self, screenshot):
        self.lock.acquire()
        self.screenshot = screenshot
        self.lock.release()

    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    # main logic controller
    def run(self):
        while not self.stopped:
            if self.state == BotState.INITIALIZING:
                # do no bot actions until the start period is complete
                if time() > self.timestamp + self.INITIALIZING_SECONDS:
                    # start searching
                    print('Searching...')
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    self.lock.release()

            elif self.state == BotState.SEARCHING:
                # check the given click point targets, confirm a fishing spot, then click it.
                success = self.click_next_target()
                # if successful, switch state to moving
                if success:
                    print('Moving...')
                    self.lock.acquire()
                    self.state = BotState.MOVING
                    self.lock.release()
                else:
                    # stay searching
                    pass
            
            elif self.state == BotState.MOVING:
                # see if we've stopped moving yet by comparing the current screenshot with the previous
                if not self.have_stopped_moving():
                    # wait a short time to allow character position to change
                    sleep(0.6)
                else:
                    # reset the timestamp marker to the current time, switch state to fishing
                    print('Fishing...')
                    self.lock.acquire()
                    self.state = BotState.FISHING
                    self.lock.release()

            elif self.state == BotState.FISHING:
                # see if invetory is full message, if it is, start dropping
                if self.inv_is_full():
                    # return to the searching state
                    self.lock.acquire()
                    self.state = BotState.DROPPING
                    self.lock.release()

                elif self.not_fishing():
                    print('Searching...')
                    self.lock.acquire()
                    self.state = BotState.SEARCHING
                    self.lock.release()
            
            elif self.state == BotState.DROPPING:
                print("Dropping...")
                # Drop all items in 3-28 slots of inventory
                self.drop_items(2, 27)

                print('Searching...')
                self.lock.acquire()
                self.state = BotState.SEARCHING
                self.lock.release()

                


    def get_screen_position(self, pos):
        return (pos[0] + self.window_offset[0], pos[1] + self.window_offset[1])



    def have_stopped_moving(self):
        # if we havent stored a screenshot yet to compare to, do that first
        if self.movement_screenshot is None:
            self.movement_screenshot = self.screenshot.copy()
            return False
        
        # compare the old screenshot to the new
        result = cv.matchTemplate(self.screenshot, self.movement_screenshot, cv.TM_CCOEFF_NORMED)
        # we only care about the value when the two screenshot are the same, so the needle position is (0, 0), 
        # since both images are the same size, this should be the only result that exists.
        similarity = result[0][0]
        # print('Movement detection similarity: {}'.format(similarity))

        if similarity >= self.MOVEMENT_STOPPED_THRESHOLD:
            # pictures look similar, so we've probably stopped moving
            print('Movement detected stop')
            return True

        # if we are still moving
        # use this new screenshot to compare to the next one
        self.movement_screenshot = self.screenshot.copy()
        return False

    def click_next_target(self):
        # 1. order targets by distance form center
        # loop:
        #   2. hover over nearest target
        #   3. confirm that it's the fishing spot via the tooltip
        #   4. if it's not, check the next target
        # endloop
        # 5. if no target was founded return False
        # 6. click on the found target and return True
        targets = self.targets_ordered_by_distance(self.targets)

        target_i = 0
        found_fish = False
        while not found_fish and target_i < len(targets):
            # if we stopped our script, exit this loop
            if self.stopped:
                break

            # load up the next target in the list and convert the coordinates
            # that are relative to the game screenshot to a position on our screen
            target_pos = targets[target_i]
            screen_x, screen_y = self.get_screen_position(target_pos)
            print('moving mouse to x:{} y:{}'.format(screen_x, screen_y))

            # move the mouse
            pyautogui.moveTo(x=screen_x, y=screen_y)
            # time for the tooltip appear
            sleep(0.8)

            # confirm fish tooltip
            if self.confirm_tooltip():
                print(f'Click on confirmed target at x:{screen_x} y:{screen_y}')
                found_fish = True
                pyautogui.click()
            target_i += 1
        
        return found_fish

    def targets_ordered_by_distance(self, targets):
        # our character is always in the center of the screen
        my_pos = (self.window_w / 2, self.window_h / 2)
        # simply uses pythagorean theorem
        # https://stackoverflow.com/a/30636138/4655368
        def pythagorean_distance(pos):
            return sqrt((pos[0] - my_pos[0])**2 + (pos[1] - my_pos[1])**2)
        targets.sort(key=pythagorean_distance)

        return targets

    def confirm_tooltip(self):
        # check the current screenshot for the fishing tooltip using match template
        result = cv.matchTemplate(self.screenshot, self.use_rod_tooltip, cv.TM_CCOEFF_NORMED)
        # Get the best match position
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if max_val >= self.TOOLTIP_MATCH_THRESHOLD:
            print('Tooltip founded')
            return True
        else:
            print('Tooltip not found')
            return False 

    def inv_is_full(self):
        # check if the current screenshot contains full inv message using match template
        result = cv.matchTemplate(self.screenshot, self.full_inventory_message, cv.TM_CCOEFF_NORMED)
        # Get the best match position
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if max_val >= self.INVENTORY_MATCH_THRESHOLD:
            print('Inventory is full, dropping')
            return True
        else:
            return False 

    def not_fishing(self):
        # wait for the display updates
        sleep(2.4)
        # check if the current screenshot contains NOT fishing message using match template
        result = cv.matchTemplate(self.screenshot, self.not_fishing_message, cv.TM_CCOEFF_NORMED)
        # Get the best match position
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if max_val >= self.NOT_FISHING_THRESHOLD:
            print('NOT Fishing detected')
            return True
        else:
            return False 

    def drop_items(self, min_range, max_range):
        inventory = [
            (580,210),(620,210),(660,210),(700,210),
            (580,250),(620,250),(660,250),(700,250),
            (580,290),(620,290),(660,290),(700,290),
            (580,330),(620,330),(660,330),(700,330),
            (580,370),(620,370),(660,370),(700,370),
            (580,400),(620,400),(660,400),(700,400),
            (580,440),(620,440),(660,440),(700,440)
        ]
        pyautogui.keyDown('shift')
        for i in range(min_range, max_range):
            pos = self.get_screen_position(inventory[i])
            inv_x, inv_y = pos
            pyautogui.moveTo(x=inv_x, y=inv_y)
            pyautogui.click()
            sleep(0.05)
        pyautogui.keyUp('shift')