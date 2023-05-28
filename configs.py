from functools import lru_cache
import pygame as pg
import os
import random
import sys

pg.mixer.init()
pg.mixer.pre_init()

def path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.normpath(os.path.join(base_path, relative_path))

def load_anm(name):
    anms = []
    num = 1
    base_path = path("assets/"+name)

    if "{}" not in base_path:
        return [base_path]
    
    while True:
        pth = base_path.format(num)
        
        if not os.path.exists(pth):
            break

        anms.append(pth)  
        num += 1

    return anms

@lru_cache(300)
def load_image(name, scale=None):
    surf = pg.image.load(path("assets/"+name))

    if scale:
        return pg.transform.scale(surf, scale)
    return surf

def load_images(name):
    return [pg.image.load(anm) for anm in load_anm(name)]

@lru_cache(1)
def load_font(size, name="fnt"):
    return pg.font.Font(path("assets/"+name+".ttf"), size)

@lru_cache()
def render(text, color=(255, 255, 255), size=19, wraplength=0):
    return load_font(size).render(text, True, color, None, wraplength)

def renders(texts, pady=5, bg=(0, 0, 0, 0)):
    wsizes = [load_font(size).size(text)[0] for text, _, size in texts]
    hsizes = [load_font(size).size("")[1]+pady for _, _, size in texts]
    
    surf = pg.Surface((max(wsizes), sum(hsizes))).convert_alpha()
    surf.fill(bg)
    
    for i, (text, color, size) in enumerate(texts):
        surf.blit(render(text, color, size), ((surf.get_size()[0]-wsizes[i])//2, sum(hsizes[:i])))

    return surf

@lru_cache()
def load_sound(name):
    return pg.mixer.Sound(path(name))

def play_sound(name, filetype="ogg"):
    load_sound("assets/"+name+"."+filetype).play()
    
class MusicManager:
    music = path("assets/bgm{}.ogg")
    music_formats = ["1", "2", "3"]
        
    def __init__(self):
        self.idx = 0
        self.running = True
        random.shuffle(self.music_formats)

    def play(self, name):
        pg.mixer.music.load(name)
        pg.mixer.music.play()
            
    def update(self):
        if not pg.mixer.music.get_busy() and self.running:
            self.play(self.music.format(self.music_formats[self.idx]))

            self.idx += 1
            if self.idx == len(self.music_formats):
                self.idx = 0

    def stop(self):
        self.running = False
        pg.mixer.music.fadeout(1000)

vec = pg.Vector2

WIDTH = 1000
HEIGHT = 600

APPNAME = "Field"
VERSION = "2.0"
MAINBGM = path("assets/main_bgm.ogg")
CREDITS = """
Created by Python-ZZY (pythonzzy@foxmail.com)

itch: https://python-zzy-china.itch.io/

github: https://github.com/Python-ZZY/

Contributor: WuxiaScrub (Game Designing and Resources)
itch: https://wuxia-scrub.itch.io/

Contributor: fywq (Game Designing)

Assets:
opengameart.org
aigei.com
www.tinyworlds.org
cooltext.com
...

Most resources come from the Internet
Please contact the creator for copyright infringement

Made with Python + Pygame
Made for Pygame Community Halloween Jam 2022

Thanks for playing!
""".replace("\n\n", "\n"*10)
