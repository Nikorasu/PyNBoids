import pygame as pg
from math import sin, cos, atan2, radians, degrees
from random import randint

#  PyNBoids by Nik - a Boids simulation
FULLSCREEN = False  # True for Fullscreen or False for Window
BOIDZ = 100         # How many boids to spawn, may slow after 100-200ish.
WRAP = False        # Wrap boids to other side of screen, otherwise avoid edge.
WIDTH = 1200        # 1200
HEIGHT = 800        # 800
FPS = 48            # 30-90

# this class handles the individual boids
class Boid(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.Surface((16, 16))  # setting up boid image
        self.image.set_colorkey((0, 0, 0))
        randcolor = (randint(55,200),randint(55,200),randint(55,200))
        pg.draw.polygon(self.image, randcolor, ((0, 2), (16, 8), (0, 14)))
        self.org_image = self.image.copy()
        self.direction = pg.Vector2(1, 0)
        self.window = pg.display.get_surface()
        w, h = self.window.get_size()
        self.rect = self.image.get_rect(center=(randint(50,w-50), randint(50,h-50)))
        self.angle = randint(0,360)
        self.pos = pg.Vector2(self.rect.center)

    def update(self, allBoids, dt): # Most boid behavior/logic done in here
        selfCenter = pg.Vector2(self.rect.center)
        turnDir = xvt = yvt = yat = xat = 0
        neiboids = sorted([  # gets list of nearby boids, sorted by distance
            iBoid for iBoid in allBoids
            if pg.Vector2(iBoid.rect.center).distance_to(selfCenter) < 200 and iBoid != self ],
            key=lambda i: pg.Vector2(i.rect.center).distance_to(selfCenter))
        del neiboids[7:]  # keep 7 closest, dump the rest
        #ncount = len(neiboids) # replaced by walrus
        if (ncount := len(neiboids)) > 1:  # when boid has neighborS
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
            angleDiff = (self.angle - tAngle) + 180
            turnDir = ((angleDiff/360 - ( angleDiff//360 )) * 360.0) - 180
            # if boid gets too close to targets, steer away
            if tDistance < 16 and targetV == nearestBoid : turnDir = -turnDir
        margin = 50
        turnRate = 3
        curW, curH = self.window.get_size()
        # Avoids edges of screen by turning toward their surface-normal
        if not WRAP and min(self.pos.x, self.pos.y, curW - self.pos.x, curH - self.pos.y) < margin:
            if self.pos.x < margin : tAngle = 0
            elif self.pos.x > curW - margin : tAngle = 180
            if self.pos.y < margin : tAngle = 90
            elif self.pos.y > curH - margin : tAngle = 270
            angleDiff = (self.angle - tAngle) + 180
            turnDir = ((angleDiff/360 - ( angleDiff//360 )) * 360.0) - 180
            edgeDist = min(self.pos.x, self.pos.y, curW - self.pos.x, curH - self.pos.y)
            turnRate = 3 + (1 - edgeDist / margin) * (20 - 3) #minRate+(1-dist/margin)*(maxRate-minRate)
        # steers based on turnDir
        if turnDir != 0:
            self.angle -= turnRate * abs(turnDir) / turnDir
            self.angle %= 360  # ensures that the angle stays within 0-360
        # adjusts angle of boid image to match heading
        self.image = pg.transform.rotate(self.org_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)  # recentering fix
        # controls forward movement/speed
        self.direction = pg.Vector2(1, 0).rotate(self.angle).normalize()
        next_pos = self.pos + self.direction * 200 * dt
        self.pos = next_pos
        # screen wrap
        if WRAP and not self.window.get_rect().contains(self.rect):
            if self.rect.bottom < 0 : self.pos.y = curH
            elif self.rect.top > curH : self.pos.y = 0
            if self.rect.right < 0 : self.pos.x = curW
            elif self.rect.left > curW : self.pos.x = 0
        # Actually update position of boid
        self.rect.center = self.pos

def main():
    pg.init()  # prepare window
    pg.display.set_caption("PyNBoids")
    try: pg.display.set_icon(pg.image.load("nboids.png"))
    except: print("FYI: nboids.png icon not found, skipping..")
    if FULLSCREEN:
        #screen = pg.display.set_mode((0,0), pg.FULLSCREEN)
        currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
        screen = pg.display.set_mode(currentRez, pg.FULLSCREEN | pg.SCALED)
        pg.display.toggle_fullscreen()  # linux workaround
        pg.mouse.set_visible(False)
    else: screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
    # spawns desired number of boids
    nBoids = pg.sprite.Group()
    for n in range(BOIDZ):
        nBoids.add(Boid())
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
        screen.fill((0, 0, 0))  # background color
        nBoids.update(allBoids, dt)
        nBoids.draw(screen)
        pg.display.update()

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
