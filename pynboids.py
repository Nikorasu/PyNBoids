import pygame
from math import sin, cos, atan2, radians, degrees
from random import randint

# Made by Nik
# This is an attempt to recreate the biods simulation myself.

WIDTH = 1200
HEIGHT = 800
FPS = 48
ICON = True

# this class handles the individual boids
class Boid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        self.image.set_colorkey((0, 0, 0)) # self.image.fill((0, 0, 0))
        randcolor = randint(50,200),randint(50,200),randint(50,200)
        pygame.draw.polygon(self.image, randcolor, ((0, 2), (16, 8), (0, 14))) # pygame.Color(
        self.org_image = self.image.copy()
        self.direction = (1, 0) # pygame.Vector2(0, -1)
        w, h = pygame.display.get_surface().get_size()
        self.rect = self.image.get_rect(center=(randint(0,w), randint(0,h))) #.get_rect(center=(w/2, h/2))
        self.angle = randint(0,360)
        self.pos = self.rect.center # pygame.Vector2(self.rect.center)

    def update(self, events, dt): # pretty much all their logic is in here
        # this bit checks all other boids to see who's nearby, and manages a list of neighbors
        #for iBoid in self.groups()[0].sprites():
        #    idist = pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(iBoid.rect.center))
        #    if (idist < 128) and (iBoid != self) and not iBoid in neiboids:
        #        neiboids.append(iBoid)
        #    elif (idist > 128) and iBoid in neiboids:
        #        neiboids.remove(iBoid)
        neiboids = pygame.sprite.spritecollide(self, self.groups()[0].sprites(), False, pygame.sprite.collide_circle_ratio(8))
        neiboids.remove(self)  # neiboids = [] # might be needed b4 these
        # ^ this alternative sometimes seems slower.. up to 1 fps slower, but other way crashes?

        # sort the neighbors by their distance to self.. hopefully works
        neiboids.sort(key=lambda i: pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(i.rect.center)))
        del neiboids[7:] # keep 7 closest, dump the rest
        # next we get the averaged center coordinate for all neighbors, storing it as targetV
        xvt = yvt = yat = xat = 0
        ncount = len(neiboids)
        if ncount > 0:
            for nBoid in neiboids:
                xvt += nBoid.rect.centerx
                yvt += nBoid.rect.centery
                yat += sin(radians(nBoid.angle))
                xat += cos(radians(nBoid.angle))

            tAvejAng = round(degrees(atan2(yat, xat)))
            # PLANS: if other boids get closer than 32, set them to target and fly away
            # also, average angles of neiboids and use when in certain range
            targetV = (xvt / ncount, yvt / ncount)
            tDiff = targetV - pygame.Vector2(self.rect.center)
            tDistance, tAngle = pygame.math.Vector2.as_polar(tDiff) #[1] angle #[0] has distance
            #if distance < 100ish but > say 32 : self.angle = targetAng
            if tDistance < 64 : tAngle = tAvejAng # + randint(-30,30)

            angleDiff = (self.angle - tAngle) + 180
            angleDiff = ((angleDiff/360 - ( angleDiff//360 )) * 360.0) - 180
            #this is slower
            #angleDiff = (self.angle - tAngle) % 360
            #if abs(angleDiff) > 180: angleDiff += angleDiff > 0 and -360 or 360
            if tDistance < 10 : angleDiff = -angleDiff

            if angleDiff < 0 : self.angle += 2
            elif angleDiff > 0 : self.angle -= 2
            self.angle %= 360
            #if self.angle > 360: self.angle = 0 + (self.angle % 360)
            #if self.angle < 0: self.angle = 360 - (-self.angle % 360)

        # adjusts angle of boid image to match heading
        self.image = pygame.transform.rotate(self.org_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center) # important fix

        self.direction = pygame.Vector2(1, 0).rotate(self.angle).normalize()
        next_pos = self.pos + self.direction * 100 * dt / 1000
        self.pos = next_pos

        window = pygame.display.get_surface().get_rect()
        # screen wrap
        if not window.contains(self.rect):
            if self.rect.centery < 0 : self.pos.y = window.h
            if self.rect.centery > window.h : self.pos.y = 0
            if self.rect.centerx < 0 : self.pos.x = window.w
            if self.rect.centerx > window.w : self.pos.x = 0
        # Actually update position of boid
        self.rect.center = self.pos

def main():
    pygame.init()
    pygame.display.set_caption("PyNBoids")
    if ICON : pygame.display.set_icon(pygame.image.load("nboids.png"))
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    nBoids = pygame.sprite.Group()
    for n in range(100): # Boid amount, 100-200 max
        nBoids.add(Boid())
    #BoidList = nBoids.sprites()
    clock = pygame.time.Clock()
    fpsDelayer = dt = 0

    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == pygame.QUIT:
                return

        screen.fill((10, 10, 10))
        nBoids.update(events, dt)
        nBoids.draw(screen)
        pygame.display.update()

        dt = clock.tick(FPS)

        fpsDelayer+=1
        if fpsDelayer>20:
            print(clock.get_fps())
            fpsDelayer=0

if __name__ == '__main__':
    main()

pygame.quit()
