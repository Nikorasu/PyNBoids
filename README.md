# PyNBoids
![Preview](preview.gif "Preview")

### A Python Boids Simulation

This is a [Boids simulation](https://en.wikipedia.org/wiki/Boids "Wikipedia"),
written in Python3, with Pygame2 and NumPy.

**To use** save the `pynboids_sp.py` file (and `nboids.png` if you want the
icon, not required) and run via python. (Example: `python3 pynboids.py`)
`Esc` key to quit.

I've included several customizable settings near the top of the code.
You can adjust window size, fullscreen, fps, and how many boids to spawn,
as well as whether they avoid the screen edges or wrap to the other side,
change the background color, or turn the boids into fish! ;)

##### Update (5/20/21):
New `pynboids_sp.py` version, implements a spatial partitioning grid to
improve efficiency of boids detecting other boids. Most efficient version
so far! For me, 420 boids at 60fps, 1000 at ~20fps. (Also, 100 commits!)

##### Update (5/16/21):
Added `pynboids2.py` version, an update to the original pynboids, with numpy
array methods from pixelboids.py to improve efficiency. 2x more boids then b4.

##### Update (5/14/21):
Added `pixelboids.py` version, draws boids as pixels in surfarray that fades
as they move. Distance sorting & for-loop math replaced with numpy array math.
Uses a fading surfArray to create tails, pixelation makes them look animated.

For more information, and future updates,
[see github page](https://github.com/Nikorasu/PyNBoids "PyNBoids").

---

        This program is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation.

        This program is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with this program.
        If not, see: https://www.gnu.org/licenses/gpl-3.0.html

###### Copyright (c) 2021  Nikolaus Stromberg - nikorasu85@gmail.com
