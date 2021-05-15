# PyNBoids

![Preview](preview.gif "Preview")

### A Python Boids Simulation

This is a [Boids simulation](https://en.wikipedia.org/wiki/Boids "Wikipedia"),
written in Python3 with Pygame2.

**To use** save the `pynboids.py` file somewhere (and `nboids.png` if you want
it's icon, not required), and run via python. (Example: `python3 pynboids.py`)
`Esc` key to quit.

I've included several tweakable settings near the top of the code. You can
adjust window size, fullscreen, fps, and how many boids to spawn, as well as
whether boids avoid screen edges or wrap to the other side.. Change the
background color, or turn the boids into fish! ;) More in the future..

##### Update (5/14/21):
New `pixelboids.py` version, draws boids as pixels in a surfarray, that fades
as they move. Distance sorting & for-loop math replaced with numpy array math.
This version should be able to handle more boids than previous ones.

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
