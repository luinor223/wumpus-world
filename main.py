import time

from agent import Agent
from program import Program
import pygame
from display_mode import PseudoAgent


def main():
    ZaWorld = Program()
    ZaWorld.create_world('input.txt')
    ZaWorld.print_world()
    dio = Agent(ZaWorld, 1, 1)
    dio.explore()
    dio.output_action_log()

    jotaro = PseudoAgent(dio.action_log, 'input.txt')

    scr_size = (800, 600)
    pygame.init()
    screen = pygame.display.set_mode(scr_size)
    fps = 12
    pyclock = pygame.time.Clock()
    toggle_fog = True

    running = True
    while running:
        pyclock.tick(fps)
        screen.fill((0, 0, 0))

        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                running = False
                break

            if events.type == pygame.KEYDOWN:
                if events.key == pygame.K_TAB:
                    toggle_fog = not toggle_fog

        jotaro.next_step()
        jotaro.display(screen, toggle_fog)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
