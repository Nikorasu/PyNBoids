from math import sin, cos, atan2, radians, degrees
from random import randint
import pygame as pg
'''
PyNBoids - a Boids simulation - github.com/Nikorasu/PyNBoids
Copyright (c) 2021  Nikolaus Stromberg  nikorasu85@gmail.com
'''
FLLSCRN = True          # True for Fullscreen, or False for Window.
BOIDZ = 32             # How many boids to spawn, may slow after 200ish.
WRAP = False            # False avoids edges, True wraps boids to other side.
FISH = True            # True here will turn boids into fish.
BGCOLOR = (0, 0, 0)     # Background color in RGB.
WIDTH = 1200            # default 1200
HEIGHT = 800            # default 800
FPS = 48                # 48-90

class Boid(pg.sprite.Sprite):
    def __init__(self, drawSurf, isFish=False, cHSV=None):
        super().__init__()
        self.image = pg.Surface((15, 15))
        self.image.set_colorkey(0)
        randColor = pg.Color(0)  # preps color for hsva
        randColor.hsva = (randint(0,360), 85, 85) if cHSV is None else cHSV # randint(10,60) goldfish
        if isFish:  # (randint(120,300) + 180) % 360 noblues
            pg.draw.polygon(self.image, randColor, ((7,0), (12,5), (3,14), (11,14), (2,5), (7,0)), width=3)
            self.image = pg.transform.scale(self.image,(18,26))
        else : pg.draw.polygon(self.image, randColor, ((7,0), (13,14), (7,11), (1,14), (7,0)))
        self.pSpace = (self.image.get_width() + self.image.get_height()) / 2
        self.org_image = pg.transform.rotate(self.image.copy(), -90)
        self.direction = pg.Vector2(1, 0)  # sets up forward directional vector
        self.drawSurf = drawSurf
        w, h = self.drawSurf.get_size()
        self.rect = self.image.get_rect(center=(randint(50, w - 50), randint(50, h - 50)))
        self.angle = randint(0, 360)  # random start angle, and position ^
        self.pos = pg.Vector2(self.rect.center)

    def update(self, allBoids, dt, ejWrap=False):  # boid behavior
        selfCenter = pg.Vector2(self.rect.center)
        curW, curH = self.drawSurf.get_size()
        turnDir = xvt = yvt = yat = xat = 0
        turnRate = 2.5 #1.5 * (dt * 100)  # dt seems to cause more spinning
        margin = 48
        neiboids = sorted([  # gets list of nearby boids, sorted by distance
            iBoid for iBoid in allBoids
            if pg.Vector2(iBoid.rect.center).distance_to(selfCenter) < self.pSpace*12 and iBoid != self ],
            key=lambda i: pg.Vector2(i.rect.center).distance_to(selfCenter)) # 200
        del neiboids[7:]  # keep 7 closest, dump the rest
        if (ncount := len(neiboids)) > 1:  # when boid has neighborS (walrus sets ncount)
            nearestBoid = pg.Vector2(neiboids[0].rect.center)
            for nBoid in neiboids:  # adds up neighbor vectors & angles for averaging
                xvt += nBoid.rect.centerx
                yvt += nBoid.rect.centery
                yat += sin(radians(nBoid.angle))
                xat += cos(radians(nBoid.angle))
            tAvejAng = degrees(atan2(yat, xat)) #round()
            targetV = (xvt / ncount, yvt / ncount)
            # if too close, move away from closest neighbor
            if selfCenter.distance_to(nearestBoid) < self.pSpace : targetV = nearestBoid
            tDiff = targetV - selfCenter  # get angle differences for steering
            tDistance, tAngle = pg.math.Vector2.as_polar(tDiff)
            # if boid is close enough to neighbors, match their average angle
            if tDistance < self.pSpace*6 : tAngle = tAvejAng # 100 #and ncount > 2
            # computes the difference to reach target angle, for smooth steering
            angleDiff = (tAngle - self.angle) + 180
            turnDir = (angleDiff / 360 - (angleDiff // 360)) * 360 - 180
            # if boid gets too close to target, steer away
            if tDistance < self.pSpace and targetV == nearestBoid : turnDir = -turnDir
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
        if turnDir != 0:  # steers based on turnDir, handles left or right
            self.angle += turnRate * abs(turnDir) / turnDir
            self.angle %= 360  # ensures that the angle stays within 0-360
        # adjusts angle of boid image to match heading
        self.image = pg.transform.rotate(self.org_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix
        self.direction = pg.Vector2(1, 0).rotate(self.angle).normalize()
        next_pos = self.pos + self.direction * (190 + (7-ncount)**2) * dt  # boid speed, 185 - 200
        self.pos = next_pos
        # optional screen wrap
        if ejWrap and not self.drawSurf.get_rect().contains(self.rect):
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
        pg.display.toggle_fullscreen()  # linux fix
        pg.mouse.set_visible(False)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
    # spawns desired number of boids
    nBoids = pg.sprite.Group()
    for n in range(BOIDZ):
        nBoids.add(Boid(screen, FISH))
    allBoids = nBoids.sprites()
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
