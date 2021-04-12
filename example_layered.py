#!/usr/bin/env python3
from pynboids import Boid
from random import randint
import pygame as pg
'''
Boid Import Example w/ layered groups.
Copyright (c) 2021  Nikolaus Stromberg
'''
BPL = 48                # How many boids per layer
FLLSCRN = False         # True for Fullscreen, or False for Window.
WRAP = False            # False avoids edges, True wraps boids to other side.
BGCOLOR = (0, 0, 48)    # Background color in RGB.
FPS = 48                # 30-90

def main():
    pg.init()
    pg.display.set_caption("Fish Tank")
    currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
    if FLLSCRN:
        screen = pg.display.set_mode(currentRez, pg.FULLSCREEN | pg.SCALED)
        pg.display.toggle_fullscreen()  #pg.HWSURFACE | pg.DOUBLEBUF
        pg.mouse.set_visible(False)
    else: screen = pg.display.set_mode(currentRez, pg.RESIZABLE)

    bg_surf = pg.Surface((currentRez[0]*1.1,currentRez[1]*1.1))
    bg_surf.set_colorkey(0)

    bg_Boids = pg.sprite.Group()
    front_Boids = pg.sprite.Group()

    for n in range(BPL):  # 4goldfish: randint(10,60)  noblues: (((randint(120,300)+180)%360),35,35)
        bg_Boids.add(Boid(bg_surf, True, (((randint(120,300) + 180) % 360),35,35)))
        front_Boids.add(Boid(screen, True, (((randint(120,300) + 180) % 360),95,95)))

    bgBoids = bg_Boids.sprites()
    frontBoids = front_Boids.sprites()

    clock = pg.time.Clock()
    while True:
        events = pg.event.get()
        for e in events:
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return
        dt = clock.tick(FPS) / 1000

        bg_surf.fill(BGCOLOR)
        screen.fill(BGCOLOR)

        bg_Boids.update(bgBoids, dt, FPS, WRAP)
        front_Boids.update(frontBoids, dt, FPS, WRAP)

        bg_Boids.draw(bg_surf)
        bg_surf2 = pg.transform.scale(bg_surf,screen.get_size())
        pg.Surface.blit(screen, bg_surf2, (0,0))
        front_Boids.draw(screen)
        pg.display.update()

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
