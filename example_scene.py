#!/usr/bin/env python3
from pynboids import Boid
from random import randint
from math import cos
import pygame as pg
'''
Boid Import Example, Fish Tank Scene.
Copyright (c) 2021  Nikolaus Stromberg
'''
BPL = 42                # How many boids per layer
FLLSCRN = True          # True for Fullscreen, or False for Window.
WRAP = False            # False avoids edges, True wraps boids to other side.
BGCOLOR = (0, 0, 48)    # Background color in RGB.
FPS = 48                # 30-90

def main():
    pg.init()
    pg.display.set_caption("Fish Tank")
    currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
    if FLLSCRN:
        screen = pg.display.set_mode(currentRez, pg.SCALED)
        pg.mouse.set_visible(False)
    else: screen = pg.display.set_mode((int(currentRez[0]*0.99),int(currentRez[1]*0.94)), pg.SCALED | pg.RESIZABLE)

    bg_surf = pg.Surface((screen.get_width()*1.1, screen.get_height()*1.1))
    bg_surf.set_colorkey(0)
    top_surf = pg.Surface((screen.get_width(), screen.get_height()))
    top_surf.set_colorkey(0)
    bg_Boids = pg.sprite.Group()
    front_Boids = pg.sprite.Group()
    # goldfish: randint(10,60)  noblues: (((randint(120,300)+180)%360),35,35)
    for n in range(BPL):
        bg_Boids.add(Boid(bg_surf, True, (((randint(120,300) + 180) % 360),35,35)))
        front_Boids.add(Boid(top_surf, True, (((randint(120,300) + 180) % 360),95,95)))
    bgBoids = bg_Boids.sprites()
    frontBoids = front_Boids.sprites()

    #Bubbles = pg.sprite.Group()
    #for b in range(10):
    #    Bubbles.add(Bubble(top_surf))

    clock = pg.time.Clock()
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return

        dt = clock.tick(FPS) / 1000

        bg_surf.fill(0)
        top_surf.fill(0)
        screen.fill(BGCOLOR)

        bg_Boids.update(bgBoids, dt, WRAP)
        #Bubbles.update(dt, FPS)
        front_Boids.update(frontBoids, dt, WRAP)

        bg_Boids.draw(bg_surf)
        bg_surf2 = pg.transform.scale(bg_surf,screen.get_size())
        #screen.blit(bg_surf2, (0,0))
        #Bubbles.draw(top_surf)
        front_Boids.draw(top_surf)
        top_surf2 = pg.transform.scale(top_surf,screen.get_size())
        #screen.blit(top_surf2, (0,0))
        screen.blits([(bg_surf2, (0,0)), (top_surf2, (0,0))])
        pg.display.update()

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
