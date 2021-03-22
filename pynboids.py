import pygame as pg
from math import sin, cos, atan2, radians, degrees
from random import randint

#  PyNBoids by Nik - WIP
# This is an attempt to recreate the Boids simulation myself.

BOIDZ = 100    # how many boids to spawn, may slow after 100-200ish
WIDTH = 1200   # 1200
HEIGHT = 800   # 800
FPS = 48       # 48 looks ok

# this class handles the individual boids
class Boid(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # set up for boid
        self.image = pg.Surface((16, 16))
        self.image.set_colorkey((0, 0, 0)) # self.image.fill((0, 0, 0))
        randcolor = (randint(64,200),randint(64,200),randint(64,200))
        pg.draw.polygon(self.image, randcolor, ((0, 2), (16, 8), (0, 14)))
        self.org_image = self.image.copy()
        self.direction = pg.Vector2(1, 0)
        w, h = pg.display.get_surface().get_size()
        self.rect = self.image.get_rect(center=(randint(0,w), randint(0,h)))
        self.angle = randint(0,360)
        self.pos = pg.Vector2(self.rect.center)

    def update(self, events, allBoids, dt): # Most boid behavior done in here
        # checks all other boids to see who's nearby, and manages a list of neighbors
        neiboids = sorted([
            iBoid for iBoid in allBoids #self.groups()[0].sprites()
            if pg.Vector2(iBoid.rect.center).distance_to(self.rect.center) < 128 and iBoid != self ],
            key=lambda i: pg.Vector2(i.rect.center).distance_to(pg.Vector2(self.rect.center)))
        #neiboids = pg.sprite.spritecollide(self, self.groups()[0].sprites(), False, pg.sprite.collide_circle_ratio(8))
        #neiboids.remove(self) # this method was SLOW
        # sort the neighbors by their distance to self.. seems to work
        #neiboids.sort(key=lambda i: pg.Vector2(self.rect.center).distance_to(pg.Vector2(i.rect.center)))
        del neiboids[7:]  # keep 7 closest, dump the rest
        # prep variables for averages
        xvt = yvt = yat = xat = 0
        #ncount = len(neiboids) # replaced by walrus
        if (ncount := len(neiboids)) > 0:  # when boid has neighbors
            for nBoid in neiboids:  # adds up neighbor vectors and angles to prepare for averaging
                xvt += nBoid.rect.centerx
                yvt += nBoid.rect.centery
                yat += sin(radians(nBoid.angle))
                xat += cos(radians(nBoid.angle))
            # computes average angle and vector for neighbors
            tAvejAng = round(degrees(atan2(yat, xat)))
            targetV = (xvt / ncount, yvt / ncount)
            # if closest neighbor is too close, set it as target to avoid
            if pg.Vector2(self.rect.center).distance_to(pg.Vector2(neiboids[0].rect.center)) < 16:
                targetV = neiboids[0].rect.center
            tDiff = targetV - pg.Vector2(self.rect.center)  # get angle differences for steering
            tDistance, tAngle = pg.math.Vector2.as_polar(tDiff)  #[1] angle #[0] has distance
            # if boid is close enough to neighbors, match their average angle
            if tDistance < 64 : tAngle = tAvejAng
            # computes the difference to reach target angle, for smooth steering
            angleDiff = (self.angle - tAngle) + 180
            angleDiff = ((angleDiff/360 - ( angleDiff//360 )) * 360.0) - 180
            # if boid gets too close to targets, steer away
            if tDistance < 16 and targetV == neiboids[0].rect.center : angleDiff = -angleDiff
            # steers based on angleDiff
            #if angleDiff < 0 : self.angle += 2
            #elif angleDiff > 0 : self.angle -= 2
            if angleDiff != 0:
                self.angle -= 2 * abs(angleDiff) / angleDiff
                self.angle %= 360  # ensures that the angle stays within 0-360
        # adjusts angle of boid image to match heading
        self.image = pg.transform.rotate(self.org_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)  # centering fix
        # controls forward movement/speed
        self.direction = pg.Vector2(1, 0).rotate(self.angle).normalize()
        next_pos = self.pos + self.direction * 200 * dt
        self.pos = next_pos
        # screen wrap
        window = pg.display.get_surface().get_rect()
        if not window.contains(self.rect):
            if self.rect.bottom < 0 : self.pos.y = window.h
            if self.rect.top > window.h : self.pos.y = 0
            if self.rect.right < 0 : self.pos.x = window.w
            if self.rect.left > window.w : self.pos.x = 0
        # Actually update position of boid
        self.rect.center = self.pos

def main():
    pg.init()  # prepare window
    pg.display.set_caption("PyNBoids")
    try: pg.display.set_icon(pg.image.load("nboids.png"))
    except: print("FYI: nboids.png icon not found, skipping..")
    screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
    # spawns desired number of boids
    nBoids = pg.sprite.Group()
    for n in range(BOIDZ):
        nBoids.add(Boid())
    allBoids = nBoids.sprites() #set() seems slower
    # clock setup
    clock = pg.time.Clock()
    # main loop
    while True:
        events = pg.event.get()
        for e in events:
            if e.type == pg.QUIT:
                return
        dt = clock.tick(FPS) / 1000
        screen.fill((10, 10, 10)) # background color
        nBoids.update(events, allBoids, dt)
        nBoids.draw(screen)
        pg.display.update()
        #fpsChecker+=1  #fpsChecker = 0  # must go before main loop
        #if fpsChecker>=FPS:  # quick debug to see fps in terminal
        #    print(round(clock.get_fps(),2))
        #    fpsChecker=0

if __name__ == '__main__':
    main()
# by Nik
pg.quit()
