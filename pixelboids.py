#!/usr/bin/env python3
from math import pi, sin, cos, atan2, radians, degrees
from random import randint
import pygame as pg
import numpy as np

#  PixelBoids - Alternate Boids drawn to surfarray, using numpy.
#  Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com

FLLSCRN = True          # True for Fullscreen, or False for Window.
BOIDZ = 100             # Number of Boids
WIDTH = 1200            # default 1200
HEIGHT = 800            # default 800
FPS = 60                # 48-90
PRATIO = 4              # Pixel Size for Pheromone grid, odds

class BoidPix():
    def __init__(self, surfArray):
        self.sArray = surfArray
        self.maxW = surfArray.surfSize[0]
        self.maxH = surfArray.surfSize[1]
        self.color = pg.Color(0)  # preps color so we can use hsva
        self.color.hsva = (randint(0,360), 85, 85)
        self.ang = randint(0, 360)  # random start angle, and position
        self.dir = pg.Vector2(1, 0).rotate(self.ang)
        self.pos = (randint(10, self.maxW - 10), randint(10, self.maxH - 10))
    def update(self, dt):
        turnDir = xvt = yvt = yat = xat = 0
        # Get list of nearby boids, sorted by distance
        neiboids = sorted([
            iBoid for iBoid in self.allBoids
            if pg.Vector2(iBoid.pos).distance_to(self.pos) < 48 and iBoid != self ],
            key=lambda i: pg.Vector2(i.pos).distance_to(self.pos))
        del neiboids[7:]  # keep 7 closest, dump the rest
        # When boid has neighborS (walrus sets ncount)
        if (ncount := len(neiboids)) > 1:
            nearestBoid = pg.Vector2(neiboids[0].pos)
            for nBoid in neiboids:  # adds up neighbor vectors & angles for averaging
                xvt += nBoid.pos[0]
                yvt += nBoid.pos[1]
                yat += sin(radians(nBoid.ang))
                xat += cos(radians(nBoid.ang))
            tAvejAng = degrees(atan2(yat, xat)) #round()
            targetV = (xvt / ncount, yvt / ncount)
            # if too close, move away from closest neighbor
            if nearestBoid.distance_to(self.pos) < 4 : targetV = nearestBoid
            tDiff = pg.Vector2(targetV) - self.pos  # get angle differences for steering
            tDistance, tAngle = pg.math.Vector2.as_polar(tDiff)
            # if boid is close enough to neighbors, match their average angle
            if tDistance < 16 : tAngle = tAvejAng # and ncount > 2
            # computes the difference to reach target angle, for smooth steering
            angleDiff = (tAngle - self.ang) + 180
            if abs(tAngle - self.ang) > 1: turnDir = (angleDiff / 360 - (angleDiff // 360)) * 360 - 180
            # if boid gets too close to target, steer away
            if tDistance < 4 and targetV == nearestBoid : turnDir = -turnDir
        # steers based on turnDir, handles left or right
        if turnDir != 0:
            self.ang += 2 * abs(turnDir) / turnDir
            self.ang %= 360  # ensures that the angle stays within 0-360

        self.dir = pg.Vector2(1, 0).rotate(self.ang).normalize()
        self.pos += self.dir * dt * (3 + (7-ncount)/14)

        # Edge Wrap
        if self.pos[1] <= 1 : self.pos[1] = self.maxH - 1
        elif self.pos[1] >= self.maxH : self.pos[1] = 1
        if self.pos[0] < 1 : self.pos[0] = self.maxW - 1
        elif self.pos[0] > self.maxW : self.pos[0] = 1

        self.sArray.img_array[(int(self.pos[0]),int(self.pos[1]))] = self.color[:3]

    def boidinput(self, boidList):
        self.allBoids = boidList

class surfaceArray():
    def __init__(self, bigSize):
        self.surfSize = (bigSize[0]//PRATIO, bigSize[1]//PRATIO)
        self.image = pg.Surface(self.surfSize).convert()
        self.img_array = np.array(pg.surfarray.array3d(self.image),dtype=float)
    def update(self, dt):
        self.img_array[self.img_array > 0] -= 24 * (60/FPS) * ((dt/10) * FPS)
        self.img_array = self.img_array.clip(0,255)
        pg.surfarray.blit_array(self.image, self.img_array)
        return self.image

def main():
    pg.init()  # prepare window
    pg.display.set_caption("PixelBoids")
    # setup fullscreen or window mode
    if FLLSCRN:  #screen = pg.display.set_mode((0,0), pg.FULLSCREEN)
        currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
        screen = pg.display.set_mode(currentRez, pg.SCALED)
        pg.mouse.set_visible(False)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT)) #, pg.RESIZABLE)

    cur_w, cur_h = screen.get_size()
    screenSize = (cur_w, cur_h)

    drawLayer = surfaceArray(screenSize)
    boidList = []
    for n in range(BOIDZ) : boidList.append(BoidPix(drawLayer))  # spawns desired # of boidz
    for n in range(BOIDZ) : boidList[n].boidinput(boidList)  # gives boids list of all boids

    clock = pg.time.Clock()
    fpsChecker = 0

    # main loop
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return

        dt = clock.tick(FPS) / 100

        screen.fill(0)

        drawImg = drawLayer.update(dt)
        rescaled_img = pg.transform.scale(drawImg, (cur_w, cur_h))
        pg.Surface.blit(screen, rescaled_img, (0,0))

        for n in range(BOIDZ): boidList[n].update(dt)

        pg.display.update()

        fpsChecker+=1  #fpsChecker = 0  # must go before main loop
        if fpsChecker>=FPS:  # quick debug to see fps in terminal
            print(round(clock.get_fps(),2))
            fpsChecker=0

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
