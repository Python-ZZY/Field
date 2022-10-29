try:
    import pyi_splash
    pyi_splash.close()
except:
    pass

import pygame as pg
import asyncio
from configs import WIDTH, HEIGHT
from scenes import Menu

async def main():
    pg.init()

    pg.display.set_mode((WIDTH, HEIGHT))

    Menu()

if __name__ == "__main__":
    asyncio.run(main())
