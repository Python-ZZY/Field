from functools import lru_cache
import pygame as pg
import os
import random
import sys

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

@lru_cache()
def load_image(name):
    return pg.image.load(path("assets/"+name))

def load_images(name):
    return [pg.image.load(anm) for anm in load_anm(name)]

@lru_cache()
def load_font(name, size):
    return pg.font.Font(path("assets/"+name+".ttf"), size)

@lru_cache()
def render(text, color=(255, 255, 255), size=14):
    return load_font("fnt", size+5).render(text, True, color)
    
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

    def update(self):
        if not pg.mixer.music.get_busy() and self.running:
            pg.mixer.music.load(self.music.format(self.music_formats[self.idx]))
            pg.mixer.music.play()

            self.idx += 1
            if self.idx == len(self.music_formats):
                self.idx = 0

    def stop(self):
        self.running = False
        pg.mixer.music.stop()

vec = pg.Vector2

WIDTH = 1000
HEIGHT = 600

APPNAME = "Field"
VERSION = "TEST 1.0"
CREDITS = """Coding by Python-ZZY
Idea Contributor: WuxiaScrub

Made with Python + Pygame
Made for Pygame Community Halloween Jam 2022

Thanks for playing :)"""
