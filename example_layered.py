#!/usr/bin/env python3
from pynboids import Boid
from random import randint
import pygame as pg
'''
Boid Import Example w/ layered groups.
Copyright (c) 2021  Nikolaus Stromberg
'''
BPL = 42                # How many boids per layer
FLLSCRN = False         # True for Fullscreen, or False for Window.
WRAP = False            # False avoids edges, True wraps boids to other side.
BGCOLOR = (0, 0, 48)    # Background color in RGB.
FPS = 48                # 30-90

def main():
    pg.init()
    pg.display.set_caption("Multilayer Test")
    currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
    if FLLSCRN:
        screen = pg.display.set_mode(currentRez, pg.FULLSCREEN | pg.SCALED)
        pg.display.toggle_fullscreen()  #pg.HWSURFACE | pg.DOUBLEBUF
        pg.mouse.set_visible(False)
    else: screen = pg.display.set_mode(currentRez, pg.RESIZABLE)

    layer1_Boids = pg.sprite.Group()
    layer2_Boids = pg.sprite.Group()
    layer3_Boids = pg.sprite.Group()

    for n in range(BPL):  # randint(10,60) goldfish
        layer1_Boids.add(Boid(screen, True, (((randint(120,300) + 180) % 360),30,30)))
        layer2_Boids.add(Boid(screen, True, (((randint(120,300) + 180) % 360),60,60)))
        layer3_Boids.add(Boid(screen, True, (((randint(120,300) + 180) % 360),90,90)))

    lyr1Boids = layer1_Boids.sprites()
    lyr2Boids = layer2_Boids.sprites()
    lyr3Boids = layer3_Boids.sprites()

    clock = pg.time.Clock()
    while True:
        events = pg.event.get()
        for e in events:
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return
        dt = clock.tick(FPS) / 1000

        screen.fill(BGCOLOR)

        layer1_Boids.update(lyr1Boids, dt, FPS, WRAP)
        layer2_Boids.update(lyr2Boids, dt, FPS, WRAP)
        layer3_Boids.update(lyr3Boids, dt, FPS, WRAP)

        layer1_Boids.draw(screen)
        layer2_Boids.draw(screen)
        layer3_Boids.draw(screen)

        pg.display.update()

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
