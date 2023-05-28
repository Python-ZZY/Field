try:
    import pyi_splash
    pyi_splash.close()
except:
    pass

import pygame as pg
import sys
from configs import WIDTH, HEIGHT
from scenes import Loading, Menu

class Stderr:
    def write(self, s, error=""):
        with open("debug.log", "a") as f:
            f.write(error + s)
sys.stderr = Stderr()

def main():
    pg.init()

    pg.display.set_mode((WIDTH, HEIGHT), pg.SCALED)

    Loading()
    Menu()

if __name__ == "__main__":
    main()
