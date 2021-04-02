import pygame as pg
from math import sin, cos, atan2, radians, degrees
from random import randint

#   PyNBoids - a Boids simulation - github.com/Nikorasu/PyNBoids
#   Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
FLLSCRN = False        # True for Fullscreen, or False for Window.
BOIDZ = 100            # How many boids to spawn, may slow after 100-200ish.
WRAP = False           # False avoids edges, True wraps boids to other side.
FISH = False           # True here will turn boids into fish.
BGCOLOR = (0, 0, 0)    # Background color in RGB.
WIDTH = 1200           # default 1200
HEIGHT = 800           # default 800
FPS = 48               # 30-90

class Boid(pg.sprite.Sprite):
    def __init__(self, isFish=False):
        super().__init__()
        self.image = pg.Surface((15, 15))  # surface to draw boid image on
        self.image.set_colorkey((0, 0, 0))  # defines black as transparent
        randColor = pg.Color(0)  # preps color variable
        randColor.hsva = (randint(0, 360), 85, 85)  # random color for each boid, randint(16,64) for goldfish
        if isFish : pg.draw.polygon(self.image, randColor, ((7,0), (12,5), (3,14), (11,14), (2,5), (7,0)), width=2)
        else : pg.draw.polygon(self.image, randColor, ((7,0), (13,14), (7,11), (1,14), (7,0)))
        self.org_image = pg.transform.rotate(self.image.copy(), -90)
        self.direction = pg.Vector2(1, 0)  # sets up forward directional vector
        self.window = pg.display.get_surface()
        w, h = self.window.get_size()
        self.rect = self.image.get_rect(center=(randint(50, w - 50), randint(50, h - 50)))
        self.angle = randint(0, 360)  # random start angle, and position ^
        self.pos = pg.Vector2(self.rect.center)

    def update(self, allBoids, dt, ejWrap=False): # most boid behavior/logic done in here
        selfCenter = pg.Vector2(self.rect.center)
        turnDir = xvt = yvt = yat = xat = 0
        neiboids = sorted([  # gets list of nearby boids, sorted by distance
            iBoid for iBoid in allBoids
            if pg.Vector2(iBoid.rect.center).distance_to(selfCenter) < 200 and iBoid != self ],
            key=lambda i: pg.Vector2(i.rect.center).distance_to(selfCenter))
        del neiboids[7:]  # keep 7 closest, dump the rest
        if (ncount := len(neiboids)) > 1:  # when boid has neighborS (also walrus sets ncount)
            nearestBoid = pg.Vector2(neiboids[0].rect.center)
            for nBoid in neiboids:  # adds up neighbor vectors and angles to prepare for averaging
                xvt += nBoid.rect.centerx
                yvt += nBoid.rect.centery
                yat += sin(radians(nBoid.angle))
                xat += cos(radians(nBoid.angle))
            # computes average angle and vector for neighbors
            tAvejAng = round(degrees(atan2(yat, xat)))
            targetV = (xvt / ncount, yvt / ncount)
            # if closest neighbor is too close, set it as target to avoid
            if selfCenter.distance_to(nearestBoid) < 16 : targetV = nearestBoid
            tDiff = targetV - selfCenter  # get angle differences for steering
            tDistance, tAngle = pg.math.Vector2.as_polar(tDiff)
            # if boid is close enough to neighbors, match their average angle
            if tDistance < 64 : tAngle = tAvejAng
            # computes the difference to reach target angle, for smooth steering
            angleDiff = (tAngle - self.angle) + 180
            turnDir = (angleDiff / 360 - (angleDiff // 360)) * 360 - 180
            # if boid gets too close to targets, steer away
            if tDistance < 16 and targetV == nearestBoid : turnDir = -turnDir
        margin = 50
        turnRate = 1.7 * (dt * 100)  # 1.7 seems to work the best for turning
        curW, curH = self.window.get_size()
        # Avoids edges of screen by turning toward their surface-normal
        if not ejWrap and min(self.pos.x, self.pos.y, curW - self.pos.x, curH - self.pos.y) < margin:
            if self.pos.x < margin : tAngle = 0
            elif self.pos.x > curW - margin : tAngle = 180
            if self.pos.y < margin : tAngle = 90
            elif self.pos.y > curH - margin : tAngle = 270
            angleDiff = (tAngle - self.angle) + 180
            turnDir = (angleDiff / 360 - (angleDiff // 360)) * 360 - 180
            edgeDist = min(self.pos.x, self.pos.y, curW - self.pos.x, curH - self.pos.y)
            turnRate = turnRate + (1 - edgeDist / margin) * (20 - turnRate) #minRate+(1-dist/margin)*(maxRate-minRate)
        # steers based on turnDir
        if turnDir != 0:  # handles left and right at the same time
            self.angle += turnRate * abs(turnDir) / turnDir
            self.angle %= 360  # ensures that the angle stays within 0-360
        # adjusts angle of boid image to match heading
        self.image = pg.transform.rotate(self.org_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix
        # controls forward movement/speed
        self.direction = pg.Vector2(1, 0).rotate(self.angle).normalize()
        next_pos = self.pos + self.direction * 200 * dt  # 200 is boid speed, 185 for fish?
        self.pos = next_pos
        # screen wrap
        if ejWrap and not self.window.get_rect().contains(self.rect):
            if self.rect.bottom < 0 : self.pos.y = curH
            elif self.rect.top > curH : self.pos.y = 0
            if self.rect.right < 0 : self.pos.x = curW
            elif self.rect.left > curW : self.pos.x = 0
        # actually update position of boid
        self.rect.center = self.pos

def main():
    pg.init()  # prepare window
    pg.display.set_caption("PyNBoids")
    try: pg.display.set_icon(pg.image.load("nboids.png"))
    except: print("FYI: nboids.png icon not found, skipping..")
    # setup fullscreen or window mode
    if FLLSCRN:  #screen = pg.display.set_mode((0,0), pg.FULLSCREEN)
        currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
        screen = pg.display.set_mode(currentRez, pg.FULLSCREEN | pg.SCALED)
        pg.display.toggle_fullscreen()  # linux workaround
        pg.mouse.set_visible(False)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
    # spawns desired number of boids
    nBoids = pg.sprite.Group()
    for n in range(BOIDZ):
        nBoids.add(Boid(FISH))
    allBoids = nBoids.sprites()
    # clock setup
    clock = pg.time.Clock()
    # main loop
    while True:
        events = pg.event.get()
        for e in events:
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return
        dt = clock.tick(FPS) / 1000
        screen.fill(BGCOLOR)
        nBoids.update(allBoids, dt, WRAP)
        nBoids.draw(screen)
        pg.display.update()

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
