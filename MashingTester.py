import pygame
from pygame.locals import *
import StateMachine as SM

class App:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Mashing Tester v0.0.3")
        pygame.joystick.init()

        self.screen = pygame.display.set_mode( (800, 600) )
        self.state_machine = SM.StateMachine()

    def main(self):
        while (True):
            events = pygame.event.get()

            for event in events:
                if (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.quit()
                    return

                elif (event.type == QUIT):
                    self.quit()
                    return

            self.state_machine.update(events)
            self.state_machine.render(self.screen)

            pygame.display.flip()

    def quit(self):
        pygame.display.quit()

app = App()
app.main()