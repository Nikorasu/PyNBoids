#!/usr/bin/env python3
from random import randint
import pygame as pg
import numpy as np
'''
PixelBoids - Pixel-based Boids simulation, drawn to a fading surfarray.
Uses numpy array math in place of math library, less for loops.
Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
'''
FLLSCRN = True          # True for Fullscreen, or False for Window
BOIDZ = 100             # Number of Boids
WIDTH = 1200            # Window Width (1200)
HEIGHT = 800            # Window Height (800)
FPS = 60                # 30-90
PRATIO = 5              # Pixel Ratio for surfArray

class BoidPix():
    def __init__(self, boidNum, surfArray):
        self.bnum = boidNum
        self.data = surfArray
        self.maxW = surfArray.surfSize[0]
        self.maxH = surfArray.surfSize[1]
        self.color = pg.Color(0)  # preps color so we can use hsva
        self.color.hsva = (randint(0, 360), 90, 90)
        self.ang = randint(0, 360)  # random start ang and pos
        self.pos = (randint(10, self.maxW - 10), randint(10, self.maxH - 10))
        self.dir = pg.Vector2(1, 0).rotate(self.ang)
    def update(self, dt):
        turnDir = xvt = yvt = yat = xat = 0
        otherBoids = np.delete(self.data.b_array, self.bnum, 0)
        # Make list of nearby boids, sorted by distance
        array_dists = (self.pos[0] - otherBoids[:,0])**2 + (self.pos[1] - otherBoids[:,1])**2
        closeBoidIs = np.argsort(array_dists)[:7]
        neiboids = otherBoids[closeBoidIs]
        neiboids[:,3] = np.sqrt(array_dists[closeBoidIs])
        neiboids = neiboids[neiboids[:,3] < 48]
        if neiboids.size > 0:  # if has neighbors, do math and sim rules
            yat = np.sum(np.sin(np.deg2rad(neiboids[:,2])))
            xat = np.sum(np.cos(np.deg2rad(neiboids[:,2])))
            # averages the positions and angles of neighbors
            tAvejAng = np.rad2deg(np.arctan2(yat, xat))
            targetV = (np.mean(neiboids[:,0]), np.mean(neiboids[:,1]))
            # if too close, move away from closest neighbor
            if neiboids[0,3] < 4 : targetV = (neiboids[0,0], neiboids[0,1])
            # get angle differences for steering
            tDiff = pg.Vector2(targetV) - self.pos
            tDistance, tAngle = pg.math.Vector2.as_polar(tDiff)
            # if boid is close enough to neighbors, match their average angle
            if tDistance < 16 : tAngle = tAvejAng
            # computes the difference to reach target angle, for smooth steering
            angleDiff = (tAngle - self.ang) + 180
            if abs(tAngle - self.ang) > 1: turnDir = (angleDiff/360 - (angleDiff//360)) * 360 - 180
            # if boid gets too close to target, steer away
            if tDistance < 4 and targetV == (neiboids[0,0], neiboids[0,1]) : turnDir = -turnDir

        # Steers based on turnDir, handles left or right
        if turnDir != 0:
            self.ang += (10 * dt) * abs(turnDir) / turnDir # turn speed 10
            self.ang %= 360  # keeps angle within 0-360
        self.dir = pg.Vector2(1, 0).rotate(self.ang).normalize()
        self.pos += self.dir * dt * (4 + (7 - neiboids.size) / 14)  # speed 3-5

        # Edge Wrap
        if self.pos[1] < 1 : self.pos[1] = self.maxH - 1
        elif self.pos[1] > self.maxH : self.pos[1] = 1
        if self.pos[0] < 1 : self.pos[0] = self.maxW - 1
        elif self.pos[0] > self.maxW : self.pos[0] = 1

        # Finally, output pos/ang to arrays
        self.data.b_array[self.bnum,:3] = [self.pos[0], self.pos[1], self.ang]
        self.data.img_array[(int(self.pos[0]), int(self.pos[1]))] = self.color[:3]

class surfaceArray():
    def __init__(self, bigSize):
        self.surfSize = (bigSize[0]//PRATIO, bigSize[1]//PRATIO)
        self.image = pg.Surface(self.surfSize).convert()
        self.img_array = np.array(pg.surfarray.array3d(self.image), dtype=float)
        self.b_array = np.zeros((BOIDZ, 4), dtype=float)
    def update(self, dt):
        self.img_array[self.img_array > 0] -= 30 * (60/FPS/1.5) * ((dt/10) * FPS)  # fade
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
    else: screen = pg.display.set_mode((WIDTH, HEIGHT))

    cur_w, cur_h = screen.get_size()
    screenSize = (cur_w, cur_h)

    drawLayer = surfaceArray(screenSize)
    boidList = []
    for n in range(BOIDZ) : boidList.append(BoidPix(n, drawLayer))  # spawns # of boidz

    clock = pg.time.Clock()

    # Main Loop
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

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
