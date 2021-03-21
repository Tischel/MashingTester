import pygame
from pygame.locals import *
from enum import Enum
import time


class State(Enum):
    CONTROLLER_SELECT = 0
    BUTTON_SELECT = 1
    MAIN = 2
    ERROR = 3

class StateMachine:
    def __init__(self):
        self.font = pygame.font.SysFont("Courier", 20, True)

        self.joystick_count = pygame.joystick.get_count()
        if self.joystick_count == 0:
            self.state = State.ERROR
        elif self.joystick_count == 1:
            self.state = State.BUTTON_SELECT
            self.joystick = pygame.joystick.Joystick(0)
        else:
            self.joystick_names = []
            for i in range(0, self.joystick_count):
                self.joystick_names.append(pygame.joystick.Joystick(i).get_name())

            self.state = State.CONTROLLER_SELECT

        self.selected_joystick_index = 0

        self.buttons = []
        self.button_is_axis = []
        self.buttons_state = []

        self.last_pressed_button = None
        self.last_pressed_button_is_axis = False

        self.test_duration = 5
        self.countdown_duration = 3
        self.reset()
        
        
    def update(self, events):
        if self.state == State.CONTROLLER_SELECT:
            for event in events:
                if (event.type == KEYUP and event.key == K_RETURN):
                    self.joystick = pygame.joystick.Joystick(self.selected_joystick_index)
                    self.joystick.init()
                    self.state = State.BUTTON_SELECT

                elif (event.type == KEYUP and event.key == K_UP):
                    self.selected_joystick_index = max(0, self.selected_joystick_index - 1)
                elif (event.type == KEYUP and event.key == K_DOWN):
                    self.selected_joystick_index = min(self.joystick_count, self.selected_joystick_index + 1)

        if self.state == State.BUTTON_SELECT:

            for b in range(0, self.joystick.get_numbuttons()):
                if self.joystick.get_button(b):
                    self.last_pressed_button = b
                    self.last_pressed_button_is_axis = False
                    break

            for a in range(4, 6):
                if round(self.joystick.get_axis(a)) == 1:
                    self.last_pressed_button = a
                    self.last_pressed_button_is_axis = True
                    break

            for event in events:
                if (event.type == KEYUP and event.key == K_RETURN):
                    if len(self.buttons) == 2:
                        self.state = State.MAIN
                    elif self.last_pressed_button is not None:
                        self.buttons.append(self.last_pressed_button)
                        self.buttons_state.append(False)
                        self.button_is_axis.append(self.last_pressed_button_is_axis)
                        self.last_pressed_button = None
                
                elif (event.type == KEYUP and event.key == K_BACKSPACE):
                    if len(self.buttons) == 2:
                        self.buttons = []
                        self.last_pressed_button = None

        elif self.state == State.MAIN:
            for event in events:
                if (event.type == KEYUP and event.key == K_RETURN):
                    if self.test_finished:
                        self.reset()
                    elif self.test_start_time is None and self.countdown_start_time is None:
                        self.countdown_start_time = time.time()
                        self.test_start_time = self.countdown_start_time + self.countdown_duration
                    
                elif (event.type == KEYUP and event.key == K_LEFT):
                    self.test_duration = max(0, self.test_duration - 1)
                elif (event.type == KEYUP and event.key == K_RIGHT):
                    self.test_duration = min(30, self.test_duration + 1)

            if self.countdown_start_time is not None:
                if time.time() > self.countdown_start_time + self.countdown_duration:
                    self.countdown_start_time = None

            if self.countdown_start_time is None and self.test_start_time is not None:
                if time.time() > self.test_start_time + self.test_duration:
                    self.test_start_time = None
                    self.test_finished = True
                    return

                button_0_down = self.isButtonPressed(0)
                button_1_down = self.isButtonPressed(1)

                # check first button
                if button_0_down == False and self.buttons_state[0] == True:
                    self.button_press_count += 1
                    if button_1_down == False:
                        self.successful_button_press_count += 1

                # check second button
                if button_1_down == False and self.buttons_state[1] == True:
                    self.button_press_count += 1
                    if button_0_down == False:
                        self.successful_button_press_count += 1

                self.buttons_state[0] = button_0_down
                self.buttons_state[1] = button_1_down

    def reset(self):
        self.countdown_start_time = None
        self.test_start_time = None
        self.button_press_count = 0
        self.successful_button_press_count = 0
        self.test_finished = False

    def render(self, screen):
        screen.fill(0)

        if self.state == State.ERROR:
            self.drawText("No controller detected", screen, screen.get_width() / 2, 20)
            self.drawText("Plug in a controller and restart the program", screen, screen.get_width() / 2, 50)
        
        elif self.state == State.CONTROLLER_SELECT:
            self.drawText("Select a controller and press ENTER to continue", screen, screen.get_width() / 2, 20)

            for i in range (0, self.joystick_count):
                prefix = "> " if i == self.selected_joystick_index else ""
                sufix = " <" if i == self.selected_joystick_index else ""
                self.drawText(prefix + self.joystick_names[i] + sufix, screen, screen.get_width() / 2, 100 + i * 20)

        elif self.state == State.BUTTON_SELECT:

            button_count = len(self.buttons)
            if button_count < 2:
                text = "first" if button_count < 1 else "second"
                self.drawText("Press the " + text + " button you want to mash with and press ENTER", screen, screen.get_width() / 2, 20)

                if self.last_pressed_button is not None:
                    self.drawText(str(self.last_pressed_button), screen, screen.get_width() / 2, 50)

            else:
                self.drawText("Press ENTER to confirm or BACKSPACE to change the buttons", screen, screen.get_width() / 2, 20)

            for i in range (0, button_count):
                self.drawText("BUTTON " + str(i+1) + " ID: " + str(self.buttons[i]), screen, screen.get_width() / 2, 100 + i * 20)

        elif self.state == State.MAIN:
            if self.countdown_start_time is not None:
                countdown = max(0, self.countdown_start_time + self.countdown_duration - time.time())
                self.drawText("STAR MASHING IN " + "{:3.1f}".format(countdown), screen, screen.get_width() / 2, 30)

            elif self.test_start_time is not None or self.test_finished:
                if self.test_start_time is not None:
                    countdown = max(0, self.test_start_time + self.test_duration - time.time())
                    self.drawText("MASH!!! (time left: " + "{:3.1f}".format(countdown) + ")", screen, screen.get_width() / 2, 30)
                elif self.test_finished:
                    self.drawText("RESULTS (press ENTER to restart)", screen, screen.get_width() / 2, 30)

                self.drawText("BUTTON PRESS COUNT: " + str(self.button_press_count), screen, screen.get_width() / 2, 100)
                self.drawText("NON-OVERLAPPED BUTTON PRESS COUNT: " + str(self.successful_button_press_count), screen, screen.get_width() / 2, 120)

                if self.test_finished:
                    self.drawText("NON-OVERLAPPED PRESSES PER SECOND: " + str(self.successful_button_press_count / self.test_duration), screen, screen.get_width() / 2, 140)
            else:
                self.drawText("Use the arrow keys to change the test duration", screen, screen.get_width() / 2, 30)
                self.drawText("TEST DURATION (seconds): " + str(self.test_duration), screen, screen.get_width() / 2, 50)
                self.drawText("Press ENTER to start the test", screen, screen.get_width() / 2, 80)

            self.drawButtons(screen)

    def drawButtons(self, screen):
        
        button_count = len(self.buttons) 
        button_pressed_count = 0
        for i in range (0, button_count):
            if self.isButtonPressed(i):
                button_pressed_count += 1

        forced_color = (200, 100, 0) if button_pressed_count == button_count else None

        self.drawButton(0, forced_color, screen, screen.get_width() / 4, 400)
        self.drawButton(1, forced_color, screen, screen.get_width() * 3/4, 400)

    def drawButton(self, button_id, forced_color, screen, x, y):
        color = forced_color
        if color is None:
            color = (0, 200, 100) if self.isButtonPressed(button_id) else (0, 100, 200)
        
        pygame.draw.circle(screen, color, (x, y), 50, 0)

        prefix = "A " if self.button_is_axis[button_id] else "B "
        self.drawText(prefix + str(self.buttons[button_id]), screen, x, y)

    def drawText(self, text, screen, x, y):
        surface = self.font.render(text, True, (255, 255, 255), (0, 0, 0))
        surface.set_colorkey((0, 0, 0))

        screen.blit(surface, (x - surface.get_width() / 2, y - surface.get_height() / 2))

    def isButtonPressed(self, button_id):
        if self.button_is_axis[button_id]:
            return round(self.joystick.get_axis(self.buttons[button_id])) == 1

        return self.joystick.get_button(self.buttons[button_id])