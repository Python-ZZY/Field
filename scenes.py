import pygame as pg
import pytmx.util_pygame as util_pygame
import json
import random
from sys import exit
from configs import *
from functions import *
from items import *
from sprites import *

TILESIZE = 32

"""TODO:
*Thunder
*Package
Ghost and bloody_screen
*Tip Msg
*Shovel
*Drop things
*Search Firewood
*Light Torch
Player Health
Player Damage
go to next lv
*view map
Ghost hurts player when it's dark!!
at last level, if player have no torch, set the screen light and show the terrible ghost image!!"""

class Scene:
    def __init__(self, screen=None, caption=None, icon=None, bg=(0, 0, 0),
                 fps=60, loop=True):
        self.screen = screen if screen else pg.display.get_surface()
        self.bg = bg
        self.fps = fps

        self.clock = pg.time.Clock()
        self.scene_running = False
        
        if caption:
            pg.display.set_caption(caption)
        if icon:
            pg.display.set_icon(icon)

        self.init()
        if loop:
            self.loop()

    def init(self):
        pass
    
    def loop(self):
        self.scene_running = True
        
        while self.scene_running:
            self.screen.fill(self.bg)
            self.update()
            self.draw()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.onexit()
                elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.onexit()
                self.events(event)
            self.draw2()
            
            self.clock.tick(self.fps)
            pg.display.update()

    def onexit(self):
        self.quit_scene()
        
    def quit_scene(self):
        self.scene_running = False

    def draw(self):
        pass

    def draw2(self):
        pass
    
    def update(self):
        pass

    def events(self, event):
        pass
                
    def wait_event(self, update=None, key=True, mouse=True):
        if not update:
            update = self.draw
            
        running = True
        while running:
            self.screen.fill(self.bg)
            update()
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    self.quitscene()
                elif event.type == pg.KEYUP and key:
                    running = False
                    return event.key
                elif event.type == pg.MOUSEBUTTONUP and mouse:
                    running = False
                    return event.pos
                
            self.clock.tick(self.fps)
            pg.display.update()

    def play_effect(self, pos, name, sound=True, frame_delta=100, kill_after_play=1,
                    **kw):
        sprite = Dynamic(0, 0, {"":name}, frame_delta=frame_delta,
                         kill_after_play=kill_after_play, **kw)
        sprite.rect.center = pos
        self.effect_sprites.add(sprite)

        if sound:
            play_sound(name.split("{")[0])

    def fade_out(self, decrease=10, draw=None):
        if not draw:
            draw = self.draw
            
        alpha = 0
        
        screenrect = self.screen.get_rect()
        background = pg.Surface((screenrect.width, screenrect.height)).convert_alpha()
        background.fill(self.bg)
        
        while True:
            draw()
            self.screen.blit(background, (0, 0))
            background.set_alpha(alpha)
            alpha += decrease
            if alpha >= 900:
                break

            pg.event.get()
            pg.display.update()
            
class Plot:
    def __init__(self):
        self.the_end = False
        self.showghosttime = 0
        self.ghost = load_image("ghost.png")
        self.ghostrect = self.ghost.get_rect(center=(WIDTH//2, HEIGHT//2))

    def plot_draw2(self):
        if self.showghosttime:
            self.screen.blit(self.ghost, self.ghostrect)
            self.showghosttime += 1
            if self.showghosttime > 40:
                self.quit_scene()
                
    def TheEnd(self):
        play_sound("the_end")
        self.mm.stop()
        self.the_end = True
        self.result = "End"
        self._update_thunder_delta()
        self.other_sprites.add(Ghost(0,  self.main_char.rect.y-40))
        
class Game(Scene, Plot):
    def __init__(self, level, package, **kw):
        self.level = level
        self.package = package

        Plot.__init__(self)
        Scene.__init__(self, **kw)
        
    def init(self):
        self.mm = MusicManager()

        self.tile_sprites = pg.sprite.Group()
        self.picked_sprites = pg.sprite.Group()
        self.obj_sprites = pg.sprite.Group()
        self.other_sprites = pg.sprite.Group()
        self.effect_sprites = pg.sprite.Group()

        self.background = None
        self.background_size = None
        
        self.main_char = None
        self.camera = vec(0, 0)
        
        self.visibility_canvas = pg.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.visibility_bubble = load_image("visibility_bubble1.png")
        self.vb_state = 1
        self.show_vb = True

        self.thundering = 0
        self.last_thunder = 0
        self._update_thunder_delta()

        self.tip = [None, None]
        self.tip_rect = None
        
        self.package_icon_start = WIDTH * 9 // 10
        self.clicked = None
        self.item_key_funcs = [eval("item_functions."+func) for func in dir(item_functions) if func.startswith("key_") ]

        self.viewer = None
        self.load_map(self.level)
        if self.level == "0":
            self.show_tip("Use Direction Keys to Control", color=(255, 0, 255))

    def _getlayer(self, mapdata, layer, tile=False):
        try:
            data = mapdata.get_layer_by_name(layer)
        except (ValueError, KeyError):
            return []
        
        if tile:
            data = data.tiles()

        return data

    def _get_background_pos(self):
        pos = vec(self.config["background"]["offset"]) - self.camera
        pos[0] *= self.config["background"]["movescale"][0]
        pos[1] *= self.config["background"]["movescale"][1]

        if pos[0] > 0:
            pos[0] = 0
        elif pos[0]+self.background_size[0] < WIDTH:
            pos[0] = WIDTH-self.background_size[0]

        if pos[1] > 0:
            pos[1] = 0
        elif pos[1]+self.background_size[1] < HEIGHT:
            pos[1] = HEIGHT-self.background_size[1]
            
        return pos
            
    def _drawsprites(self, group):
        for sprite in group.sprites():
            self.screen.blit(sprite.image, vec(sprite.rect.topleft)-self.camera)

    def _drawtip(self):
        if self.tip[0]:
            self.screen.blit(self.tip[0], self.tip_rect)
            
    def _update_thunder_delta(self):
        if self.the_end:
            self.thunder_delta = 2000
        else:
            self.thunder_delta = random.randrange(20000, 35000)
        
    def load_map(self, lvname):
        mapdata = util_pygame.load_pygame(path(f"levels/{lvname}/map.tmx"))
        self.background = pg.image.load(path(f"levels/{lvname}/background.png")).convert()
        self.config = json.load(open(path(f"levels/{lvname}/config.json")))
        self.hide = self._getlayer(mapdata, "hide")
        
        for x, y, surf in self._getlayer(mapdata, "tile", tile=True):
            self.tile_sprites.add(Static(x*TILESIZE, y*TILESIZE, surf, pgim=True))
            
        for obj in self._getlayer(mapdata, "main_char"):
            self.main_char = MainChar(obj.x, obj.y)
            self.main_char.game = self
            
        for obj in self._getlayer(mapdata, "picked"):
            sprite = StaticObject(obj, floated=[(0, 0, 0), (-5, 5, 1), 60])
            sprite.picked = True
            self.picked_sprites.add(sprite)
            
        for obj in self._getlayer(mapdata, "object"):
            if hasattr(obj, "dynamic"):
                self.obj_sprites.add(DynamicObject(obj))
            else:
                self.obj_sprites.add(StaticObject(obj))

        self.map_size = (mapdata.width*TILESIZE, mapdata.height*TILESIZE)
        self.background_size = self.background.get_rect().size

    def show_tip(self, text, time=100, color=(255, 255, 255)):
        if (time == 1 and self.tip[1]) or (not text): # time==1 means it's a low-level tip
            return
        tip = render(text, color=color)
        self.tip = [tip, time]
        self.tip_rect = tip.get_rect(center=(WIDTH//2, 200))

    def gain(self, thing, count=1):
        if count > 0:
            if hasattr(item_functions, thing):
                func = eval("item_functions."+thing)
            else:
                func = lambda *args:...
                func.__doc__ = get_name(thing)
                
            self.package[thing][0] = self.package.setdefault(
                thing, [0, load_image(thing+"_icon.png"), func]
                )[0] + count
        elif count < 0:
            self.package[thing][0] += count

            if self.package[thing][0] == 0:
                del self.package[thing]

    def hasitem(self, thing, count=1):
        if self.package.get(thing) and self.package[thing][0] >= count:
            return True

    def view(self, name, image):
        image = load_image(image)
        self.viewer = image, image.get_rect(center=(WIDTH//2, HEIGHT//2)), name

    def onexit(self):
        self.result = "Quit"
        self.mm.stop()
        self.fade_out()
        self.quit_scene()
        
    def events(self, event):    
        self.main_char.events(event)
        
        if event.type == pg.KEYDOWN:
            self.viewer = None
            
            if event.key == pg.K_SPACE and self.obj_col:
                for obj in self.obj_col:
                    obj.kspace(self)
            else:
                for func in self.item_key_funcs:
                    func(self, event.key)
                    
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                self.clicked = event.pos
        
    def draw(self):
        self.screen.blit(self.background, self._get_background_pos())
        self._drawsprites(self.tile_sprites)
        self._drawsprites(self.picked_sprites)
        self._drawsprites(self.obj_sprites)
        self.main_char.draw()
        self._drawsprites(self.other_sprites)
        self._drawsprites(self.effect_sprites)

        # EFFECT ANMS
        for sprite in self.effect_sprites:
            sprite.animate()

        # VISIBILITY BUBBLE
        if self.show_vb:
            vbrect = self.visibility_bubble.get_rect(center=self.main_char.rect.center)
            pos = vbrect.topleft-self.camera
            self.visibility_canvas.set_clip((pos[0], pos[1], vbrect.width, vbrect.height))
            self.visibility_canvas.fill((0, 0, 0, 0))
            self.visibility_canvas.blit(self.visibility_bubble, pos)
            self.screen.blit(self.visibility_canvas, (0, 0))

        # PICKED
        col = pg.sprite.spritecollide(self.main_char, self.picked_sprites, False)
        if col:
            self.show_tip("Press <Spacebar> to pick it up", 1)
            for obj in col:
                self.obj_col.append(obj)

        # PACKAGE ITEMS
        for i, (thing, (count, icon, func)) in enumerate(self.package.copy().items()):
            pos = self.package_icon_start - i*100

            if count:
                self.screen.blit(icon, (pos, 30))
                self.screen.blit(render("x"+str(count), size=10), (pos+30, 50))
                if pg.Rect(pos, 30, 45, 45).collidepoint(self.pos):
                    if ":" in func.__doc__:
                        cdt, tip = func.__doc__.split(":")
                        if eval(cdt):
                            self.show_tip(tip, 2)
                    else:
                        self.show_tip(func.__doc__, 2)
                        
                    if self.clicked:
                        self.clicked = None
                        func(self)

        # IMAGE VIEWER
        if self.viewer:
            self.screen.blit(*self.viewer[:-1])

    def draw2(self):
        self._drawtip()
        self.plot_draw2()
        
    def update(self):
        now = pg.time.get_ticks()
        self.pos = pg.mouse.get_pos()
        
        self.mm.update()
        self.other_sprites.update(self)
        self.main_char.update()
        self.picked_sprites.update()
        item_functions.update(self)

        self.camera = vec(set_threshold(self.main_char.rect.x-WIDTH//2, 0, self.map_size[0]-WIDTH),
                          set_threshold(self.main_char.rect.y-HEIGHT//2, -500, self.map_size[1]-HEIGHT))

        if self.main_char.rect.left - self.camera[0] < 0:
            self.main_char.rect.left = 0 - self.camera[0]
        elif self.main_char.rect.right - self.camera[0] > WIDTH:
            self.main_char.rect.right = WIDTH + self.camera[0]

        if self.tip[1] != None:
            self.tip[1] -= 1
            if self.tip[1] == 0:
                self.tip = [None, None]
                
        self.show_vb = True
        if now - self.last_thunder > self.thunder_delta:
            self._update_thunder_delta()
            self.last_thunder = now
            self.thundering = 1
            play_sound("thunder")
        if self.thundering:
            if self.thundering % 5 != 0:
                self.show_vb = False
                
            self.thundering += 1
            if self.thundering > 30:
                self.thundering = 0

        for state, v in enumerate((75, 50, 25, 0, -10), start=1):
            if self.main_char.torch_life > v:
                if self.vb_state != state:
                    self.vb_state = state
                    self.visibility_bubble = load_image(f"visibility_bubble{state}.png")
                break

        self.obj_col = pg.sprite.spritecollide(self.main_char, self.obj_sprites, False)[::-1] # show the newest
        for obj in self.obj_col:
            if obj.enter(self):
                break

        self.effect_sprites.update()

class EndScene(Scene):
    def __init__(self):
        super().__init__(loop=False)
        self.wait_event()
        self.onexit()
        
    def init(self):
        self.image = render("The END", (255, 0, 0))
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def onexit(self):
        self.fade_out()
        self.quit_scene()
        
class CreditsScene(Scene):
    def init(self):
        self.group = []
        self.speed = 2

        i = 0
        for text in CREDITS.split("\n"):
            if text == "\n":
                i += 2
                continue
            
            sprite = render(text)
            self.group.append([sprite, sprite.get_rect(centerx=WIDTH//2,
                                                       y=HEIGHT+i*50)])
            i += 1

    def draw(self):
        for i, (sprite, rect) in enumerate(self.group):
            if rect.y < HEIGHT:
                self.screen.blit(sprite, rect)
                
            rect.y -= self.speed
            if rect.bottom < 0:
                self.group.pop(i)

    def onexit(self):
        self.fade_out()
        self.quit_scene()
        
    def update(self):
        if len(self.group) == 0:
            self.onexit()
            
class Menu(Scene):
    def __init__(self):
        super().__init__(caption=APPNAME, icon=load_image("icon.ico"))

    def init(self):
        self.background = load_image("background.png")
        self.click = False
        
        buttons = ("Play", "Credits", "Exit")
        self.group = pg.sprite.Group()
        for i, text in enumerate(buttons):
            self.group.add(Button((WIDTH//2, 200+i*50), text, eval(f"self.{text}")))

    def events(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.click = True
            play_sound("click")

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.group.draw(self.screen)

    def update(self):
        pos = pg.mouse.get_pos()
        self.group.update(pos, self.click)
        
    def Play(self):
        self.click = False
        self.fade_out()

        package = {}
        g = Game("0", package)

        while True:
            if g.result == "Quit":
                break
            elif g.result == "End":
                EndScene()
                CreditsScene()
                break
            g = Game(g.result, g.package)

    def Credits(self):
        self.click = False
        self.fade_out()
        CreditsScene()

    def Exit(self):
        exit()
    
