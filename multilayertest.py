from pynboids import Boid
from random import randint
import pygame as pg
'''
Multilayer Boids test
Copyright (c) 2021  Nikolaus Stromberg
'''
BPL = 12              # How many boids per layer
WRAP = True            # False avoids edges, True wraps boids to other side.
BGCOLOR = (0, 0, 42)    # Background color in RGB.
FPS = 48                # 30-90

def main():
    pg.init()  # prepare window
    pg.display.set_caption("Multilayer Test")

    currentRez = (pg.display.Info().current_w, pg.display.Info().current_h)
    screen = pg.display.set_mode(currentRez, pg.FULLSCREEN | pg.SCALED) #pg.HWSURFACE | pg.DOUBLEBUF |
    pg.display.toggle_fullscreen()  # linux workaround
    pg.mouse.set_visible(False)

    #layer1_surf = pg.Surface(currentRez)
    #layer2_surf = pg.Surface(currentRez)
    #layer3_surf = pg.Surface(currentRez)
    #layer1_surf.set_colorkey(0)
    #layer2_surf.set_colorkey(0)
    #layer3_surf.set_colorkey(0)

    layer1_Boids = pg.sprite.Group()
    layer2_Boids = pg.sprite.Group()
    layer3_Boids = pg.sprite.Group()

    for n in range(BPL):
        #randColor.hsva = (((randint(120,300) + 180) % 360),85,85) # randint(10,60) goldfish
        layer1_Boids.add(Boid(screen, True, (((randint(120,300) + 180) % 360),50,33)))
        layer2_Boids.add(Boid(screen, True, (((randint(120,300) + 180) % 360),64,66)))
        layer3_Boids.add(Boid(screen, True, (((randint(120,300) + 180) % 360),80,99)))

    lyr1Boids = layer1_Boids.sprites()
    lyr2Boids = layer2_Boids.sprites()
    lyr3Boids = layer3_Boids.sprites()

    clock = pg.time.Clock()
    # main loop
    while True:
        events = pg.event.get()
        for e in events:
            if e.type == pg.QUIT or e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE:
                return
        dt = clock.tick(FPS) / 1000

        screen.fill(BGCOLOR)
        #layer1_surf.fill(0)
        #layer2_surf.fill(0)
        #layer3_surf.fill(0)

        layer1_Boids.update(lyr1Boids, dt, WRAP)
        layer2_Boids.update(lyr2Boids, dt, WRAP)
        layer3_Boids.update(lyr3Boids, dt, WRAP)

        layer1_Boids.draw(screen)#layer1_surf)
        layer2_Boids.draw(screen)#layer2_surf)
        layer3_Boids.draw(screen)#layer3_surf)

        #pg.Surface.blit(screen, layer1_surf, (0,0))
        #pg.Surface.blit(screen, layer2_surf, (0,0))
        #pg.Surface.blit(screen, layer3_surf, (0,0))

        pg.display.update()

if __name__ == '__main__':
    main()  # by Nik
    pg.quit()
