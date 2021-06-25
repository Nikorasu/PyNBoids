#!/usr/bin/env python3
from math import pi, sin, cos, atan2, radians, degrees
from random import randint
import pygame as pg

'''
PyNBoids - a Boids simulation - github.com/Nikorasu/PyNBoids
This version uses a spatial partitioning grid to improve performance.
Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
'''
FLLSCRN = True          # True for Fullscreen, or False for Window
BOIDZ = 200             # How many boids to spawn, too many may slow fps
WRAP = False            # False avoids edges, True wraps to other side
FISH = False            # True to turn boids into fish
SPEED = 150             # Movement speed
WIDTH = 1200            # Window Width (1200)
HEIGHT = 800            # Window Height (800)
BGCOLOR = (0, 0, 0)     # Background color in RGB
FPS = 60                # 30-90
SHOWFPS = False         # frame rate debug


class Boid(pg.sprite.Sprite):

    def __init__(self, grid, drawSurf, isFish=False, cHSV=None):
        super().__init__()
        self.grid = grid
        self.drawSurf = drawSurf
        self.image = pg.Surface((15, 15)).convert()
        self.image.set_colorkey(0)
        self.color = pg.Color(0)  # preps color so we can use hsva
        self.color.hsva = (randint(0,360), 90, 90) if cHSV is None else cHSV # randint(5,55) #4goldfish
        if isFish:  # (randint(120,300) + 180) % 360  #4noblues
            pg.draw.polygon(self.image, self.color, ((7,0),(12,5),(3,14),(11,14),(2,5),(7,0)), width=3)
            self.image = pg.transform.scale(self.image, (16, 24))
        else : pg.draw.polygon(self.image, self.color, ((7,0), (13,14), (7,11), (1,14), (7,0)))
        self.bSize = 22 if isFish else 17
        self.orig_image = pg.transform.rotate(self.image.copy(), -90)
        self.dir = pg.Vector2(1, 0)  # sets up forward direction
        maxW, maxH = self.drawSurf.get_size()
        self.rect = self.image.get_rect(center=(randint(50, maxW - 50), randint(50, maxH - 50)))
        self.ang = randint(0, 360)  # random start angle, & position ^
        self.pos = pg.Vector2(self.rect.center)
        self.grid_lastpos = self.grid.getcell(self.pos)
        self.grid.add(self, self.grid_lastpos)

    def update(self, dt, speed, ejWrap=False):
        maxW, maxH = self.drawSurf.get_size()
        selfCenter = pg.Vector2(self.rect.center)
        turnDir = xvt = yvt = yat = xat = 0
        turnRate = 120 * dt  # about 120 seems ok
        margin = 42
        # Grid update stuff
        self.grid_pos = self.grid.getcell(self.pos)
        if self.grid_pos != self.grid_lastpos:
            self.grid.add(self, self.grid_pos)
            self.grid.remove(self, self.grid_lastpos)
            self.grid_lastpos = self.grid_pos
        # get nearby boids and sort by distance
        near_boids = self.grid.getnear(self, self.grid_pos)
        neiboids = sorted(near_boids, key=lambda i: pg.Vector2(i.rect.center).distance_to(selfCenter))
        del neiboids[7:]  # keep 7 closest, dump the rest
        # when boid has neighborS (walrus sets ncount)
        if (ncount := len(neiboids)) > 1:
            nearestBoid = pg.Vector2(neiboids[0].rect.center)
            for nBoid in neiboids:  # adds up neighbor vectors & angles for averaging
                xvt += nBoid.rect.centerx
                yvt += nBoid.rect.centery
                yat += sin(radians(nBoid.ang))
                xat += cos(radians(nBoid.ang))
            tAvejAng = degrees(atan2(yat, xat))
            targetV = (xvt / ncount, yvt / ncount)
            # if too close, move away from closest neighbor
            if selfCenter.distance_to(nearestBoid) < self.bSize : targetV = nearestBoid
            tDiff = targetV - selfCenter  # get angle differences for steering
            tDistance, tAngle = pg.math.Vector2.as_polar(tDiff)
            # if boid is close enough to neighbors, match their average angle
            if tDistance < self.bSize*5 : tAngle = tAvejAng
            # computes the difference to reach target angle, for smooth steering
            angleDiff = (tAngle - self.ang) + 180
            if abs(tAngle - self.ang) > .5: turnDir = (angleDiff / 360 - (angleDiff // 360)) * 360 - 180
            # if boid gets too close to target, steer away
            if tDistance < self.bSize and targetV == nearestBoid : turnDir = -turnDir
        # Avoid edges of screen by turning toward the edge normal-angle
        sc_x, sc_y = self.rect.centerx, self.rect.centery
        if not ejWrap and min(sc_x, sc_y, maxW - sc_x, maxH - sc_y) < margin:
            if sc_x < margin : tAngle = 0
            elif sc_x > maxW - margin : tAngle = 180
            if sc_y < margin : tAngle = 90
            elif sc_y > maxH - margin : tAngle = 270
            angleDiff = (tAngle - self.ang) + 180  # increase turnRate to keep boids on screen
            turnDir = (angleDiff / 360 - (angleDiff // 360)) * 360 - 180
            edgeDist = min(sc_x, sc_y, maxW - sc_x, maxH - sc_y)
            turnRate = turnRate + (1 - edgeDist / margin) * (20 - turnRate) #turnRate=minRate, 20=maxRate
        if turnDir != 0:  # steers based on turnDir, handles left or right
            self.ang += turnRate * abs(turnDir) / turnDir
            self.ang %= 360  # ensures that the angle stays within 0-360
        # Adjusts angle of boid image to match heading
        self.image = pg.transform.rotate(self.orig_image, -self.ang)
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix
        self.dir = pg.Vector2(1, 0).rotate(self.ang).normalize()
        self.pos += self.dir * dt * (speed + (7 - ncount) * 5)  # movement speed
        # Optional screen wrap
        if ejWrap and not self.drawSurf.get_rect().contains(self.rect):
            if self.rect.bottom < 0 : self.pos.y = maxH
            elif self.rect.top > maxH : self.pos.y = 0
            if self.rect.right < 0 : self.pos.x = maxW
            elif self.rect.left > maxW : self.pos.x = 0
        # Actually update position of boid
        self.rect.center = self.pos


class BoidGrid():  # tracks boids in spatial partition grid

    def __init__(self):
        self.grid_size = 100
        self.dict = {}
    # finds the grid cell corresponding to given pos
    def getcell(self, pos):
        return (pos[0]//self.grid_size, pos[1]//self.grid_size)
    # boids add themselves to cells when crossing into new cell
    def add(self, boid, key):
        if key in self.dict:
            self.dict[key].append(boid)
        else:
            self.dict[key] = [boid]
    # they also remove themselves from the previous cell
    def remove(self, boid, key):
        if key in self.dict and boid in self.dict[key]:
            self.dict[key].remove(boid)
    # Returns a list of nearby boids within all surrounding 9 cells
    def getnear(self, boid, key):
        if key in self.dict:
            nearby = []
            for x in (-1, 0, 1):
                for y in (-1, 0, 1):
                    nearby += self.dict.get((key[0] + x, key[1] + y), [])
            nearby.remove(boid)
        return nearby


def main():
    pg.init()  # prepare window
    pg.display.set_caption("PyNBoids")
    try: pg.display.set_icon(pg.image.load("nboids.png"))
    except: print("Note: nboids.png icon not found, skipping..")
    # setup fullscreen or window mode
    if FLLSCRN:
        currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
        screen = pg.display.set_mode(currentRez, pg.SCALED | pg.NOFRAME | pg.FULLSCREEN, vsync=1)
        pg.mouse.set_visible(False)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE | pg.SCALED, vsync=1)

    boidTracker = BoidGrid()
    nBoids = pg.sprite.Group()
    # spawns desired # of boidz
    for n in range(BOIDZ) : nBoids.add(Boid(boidTracker, screen, FISH))

    if SHOWFPS : font = pg.font.Font(None, 30)
    clock = pg.time.Clock()

    # main loop
    while True:
        for e in pg.event.get():
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return

        dt = clock.tick(FPS) / 1000
        screen.fill(BGCOLOR)
        # update boid logic, then draw them
        nBoids.update(dt, SPEED, WRAP)
        nBoids.draw(screen)
        # if true, displays the fps in the upper left corner, for debugging
        if SHOWFPS : screen.blit(font.render(str(int(clock.get_fps())), True, [0,200,0]), (8, 8))

        pg.display.update()

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
