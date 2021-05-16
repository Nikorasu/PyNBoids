#!/usr/bin/env python3
from random import randint
import pygame as pg
import numpy as np
'''
PyNBoids - a Boids simulation - github.com/Nikorasu/PyNBoids
Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
'''
FLLSCRN = True          # True for Fullscreen, or False for Window.
BOIDZ = 150             # How many boids to spawn, too many may slow fps.
WRAP = False            # False avoids edges, True wraps to other side.
FISH = False            # True here will turn boids into fish.
BGCOLOR = (0, 0, 0)     # Background color in RGB.
WIDTH = 1200            # Window Width (1200)
HEIGHT = 800            # Window Height (800)
FPS = 48                # 30-90
SHOWFPS = False         # frame rate debug

class Boid(pg.sprite.Sprite):
    def __init__(self, boidNum, data, drawSurf, isFish=False, cHSV=None):
        super().__init__()
        self.data = data
        self.bnum = boidNum
        self.drawSurf = drawSurf
        self.image = pg.Surface((15, 15))
        self.image.set_colorkey(0)
        self.color = pg.Color(0)  # preps color so we can use hsva
        self.color.hsva = (randint(0,360), 90, 90) if cHSV is None else cHSV # randint(5,55) #4goldfish
        if isFish:  # (randint(120,300) + 180) % 360  #4noblues
            pg.draw.polygon(self.image, self.color, ((7,0),(12,5),(3,14),(11,14),(2,5),(7,0)), width=3)
            self.image = pg.transform.scale(self.image, (16, 24))
        else : pg.draw.polygon(self.image, self.color, ((7,0), (13,14), (7,11), (1,14), (7,0)))
        self.bSize = (self.image.get_width() + self.image.get_height()) / 2
        self.orig_image = pg.transform.rotate(self.image.copy(), -90)
        self.dir = pg.Vector2(1, 0)  # sets up forward direction
        maxW, maxH = self.drawSurf.get_size()
        self.rect = self.image.get_rect(center=(randint(50, maxW - 50), randint(50, maxH - 50)))
        self.ang = randint(0, 360)  # random start angle, & position ^
        self.pos = pg.Vector2(self.rect.center)
    def update(self, allBoids, dt, ejWrap=False):  # boid behavior
        maxW, maxH = self.drawSurf.get_size()
        turnDir = xvt = yvt = yat = xat = 0
        turnRate = 120 * dt  # about 120 seems ok
        margin = 42
        otherBoids = np.delete(self.data.array, self.bnum, 0)
        # Make list of nearby boids, sorted by distance
        array_dists = (self.pos.x - otherBoids[:,0])**2 + (self.pos.y - otherBoids[:,1])**2
        closeBoidIs = np.argsort(array_dists)[:7]
        neiboids = otherBoids[closeBoidIs]
        neiboids[:,3] = np.sqrt(array_dists[closeBoidIs])
        neiboids = neiboids[neiboids[:,3] < self.bSize*12]
        if neiboids.size > 1:  # if has neighborS, do math and sim rules
            yat = np.sum(np.sin(np.deg2rad(neiboids[:,2])))
            xat = np.sum(np.cos(np.deg2rad(neiboids[:,2])))
            # averages the positions and angles of neighbors
            tAvejAng = np.rad2deg(np.arctan2(yat, xat))
            targetV = (np.mean(neiboids[:,0]), np.mean(neiboids[:,1]))
            # if too close, move away from closest neighbor
            if neiboids[0,3] < self.bSize : targetV = (neiboids[0,0], neiboids[0,1])
            # get angle differences for steering
            tDiff = pg.Vector2(targetV) - self.pos
            tDistance, tAngle = pg.math.Vector2.as_polar(tDiff)
            # if boid is close enough to neighbors, match their average angle
            if tDistance < self.bSize*6 : tAngle = tAvejAng
            # computes the difference to reach target angle, for smooth steering
            angleDiff = (tAngle - self.ang) + 180
            if abs(tAngle - self.ang) > 1.2: turnDir = (angleDiff / 360 - (angleDiff // 360)) * 360 - 180
            # if boid gets too close to target, steer away
            if tDistance < self.bSize and targetV == (neiboids[0,0], neiboids[0,1]) : turnDir = -turnDir
        # Avoids edges of screen by turning toward their surface-normal
        if not ejWrap and min(self.pos.x, self.pos.y, maxW - self.pos.x, maxH - self.pos.y) < margin:
            if self.pos.x < margin : tAngle = 0
            elif self.pos.x > maxW - margin : tAngle = 180
            if self.pos.y < margin : tAngle = 90
            elif self.pos.y > maxH - margin : tAngle = 270
            angleDiff = (tAngle - self.ang) + 180  # if in margin, increase turnRate to ensure stays on screen
            turnDir = (angleDiff / 360 - (angleDiff // 360)) * 360 - 180
            edgeDist = min(self.pos.x, self.pos.y, maxW - self.pos.x, maxH - self.pos.y)
            turnRate = turnRate + (1 - edgeDist / margin) * (20 - turnRate) #minRate+(1-dist/margin)*(maxRate-minRate)
        if turnDir != 0:  # steers based on turnDir, handles left or right
            self.ang += turnRate * abs(turnDir) / turnDir
            self.ang %= 360  # ensures that the angle stays within 0-360
        # Adjusts angle of boid image to match heading
        self.image = pg.transform.rotate(self.orig_image, -self.ang)
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix
        self.dir = pg.Vector2(1, 0).rotate(self.ang).normalize()
        self.pos += self.dir * dt * (160 + (7 - neiboids.size) * 2)  # default speed 160
        # Optional screen wrap
        if ejWrap and not self.drawSurf.get_rect().contains(self.rect):
            if self.rect.bottom < 0 : self.pos.y = maxH
            elif self.rect.top > maxH : self.pos.y = 0
            if self.rect.right < 0 : self.pos.x = maxW
            elif self.rect.left > maxW : self.pos.x = 0
        # Actually update position of boid
        self.rect.center = self.pos
        # Finally, output pos/ang to array
        self.data.array[self.bnum,:3] = [self.pos[0], self.pos[1], self.ang]

class BoidArray():  # Holds array to store positions and angles
    def __init__(self):
        self.array = np.zeros((BOIDZ, 4), dtype=float)

def main():
    pg.init()  # prepare window
    pg.display.set_caption("PyNBoids")
    try: pg.display.set_icon(pg.image.load("nboids.png"))
    except: print("FYI: nboids.png icon not found, skipping..")
    # setup fullscreen or window mode
    if FLLSCRN:
        currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
        screen = pg.display.set_mode(currentRez, pg.SCALED)
        pg.mouse.set_visible(False)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)

    nBoids = pg.sprite.Group()
    dataArray = BoidArray()
    for n in range(BOIDZ):
        nBoids.add(Boid(n, dataArray, screen, FISH))  # spawns desired # of boidz
    allBoids = nBoids.sprites()

    clock = pg.time.Clock()
    if SHOWFPS : font = pg.font.Font(None, 30)

    # main loop
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return

        dt = clock.tick(FPS) / 1000
        screen.fill(BGCOLOR)
        nBoids.update(allBoids, dt, WRAP)
        nBoids.draw(screen)

        if SHOWFPS:
            screen.blit(font.render(str(int(clock.get_fps())), True, [0,200,0]), (8, 8))

        pg.display.update()

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
