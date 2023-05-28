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
            pg.display.flip()

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
                elif event.type == pg.KEYDOWN and key:
                    running = False
                    return event.key
                elif event.type == pg.MOUSEBUTTONDOWN and mouse:
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

    def fade_out(self, decrease=5, draw=None, alpha=0):
        if not draw:
            draw = self.draw
            
        alpha = alpha
        
        screenrect = self.screen.get_rect()
        background = pg.Surface((screenrect.width, screenrect.height)).convert_alpha()
        background.fill(self.bg)
        
        while True:
            draw()
            self.screen.blit(background, (0, 0))
            background.set_alpha(alpha)
            alpha += decrease
            if alpha >= 255:
                break

            pg.event.get()
            pg.display.update()

class Talk(Scene):
    def __init__(self, draw, plot, msg):
        self.gdraw = draw
        self.plot = plot
        self.msg = []
        self.index = 0

        pad = 10
        photosize = 128
        self.msgpos = (0, HEIGHT - photosize)
        bg = pg.Surface((WIDTH, photosize)).convert_alpha()
        bg.fill((0, 0, 0, 150))
        for content in msg.split("\n"):
            try:
                speaker, sentence = content.split(";")
                color = (255, 255, 255)
            except ValueError:
                speaker, sentence, color = content.split(";")
            if speaker == "sound":
                self.msg.append(sentence)
                continue
            elif speaker == "plot":
                self.msg.append(getattr(self.plot, sentence))
                continue
            surf = bg.copy()
            r = render(sentence.replace("/", "\n"), wraplength=WIDTH - photosize - 2 * pad,
                       color=color)
            surf.blit(load_image("talk_"+speaker+".png"), (0, 0))
            surf.blit(r, (photosize + pad, pad))
            self.msg.append(surf)
            
        Scene.__init__(self)

    def next(self):
        self.index += 1
        if self.index == len(self.msg):
            self.quit_scene()
            self.index = -1
    
    def events(self, event):
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_SPACE, pg.K_RETURN):
                self.next()
                play_sound("click")
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == pg.BUTTON_LEFT:
                self.next()
                play_sound("click")
                
    def draw(self):
        self.gdraw(False)
        con = self.msg[self.index]
        try:
            self.screen.blit(con, self.msgpos)
        except TypeError:
            if type(con) == str:
                play_sound(con)
            else:
                con()
            self.next()

class Plot:
    def __init__(self):
        self.the_end = False
        self.showghosttime = 0
        self.ghost = load_image("ghost.png")
        self.ghostrect = self.ghost.get_rect(center=(WIDTH//2, HEIGHT//2))

        self.check_the_body = False
        self.check_body_pos = [(545, 181), (527, 214), (532, 295), (479, 298), (577, 421)]

        self.open_pwd_gate = False
        self.typed_pwd = ""
        self.pwd_correct = "31415926"

    def plot_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.check_the_body and self.check_the_body != -1:
                found = False
                for pos in self.check_body_pos:
                    if get_dist(event.pos, pos) < 10:
                        self.check_body_pos.remove(pos)
                        found = True
                        break

                self.check_the_body = False
                if len(self.check_body_pos) == 0:
                    self.check_the_body = -1
                    self.doitem("parchment_pwd", 1)
                    self.show_tip("Ohh! Something drops out", 100, (255, 0, 0))
                elif found:
                    self.show_tip("You find a soft spot that can be pushed in slightly", 100, (255, 0, 0))
                else:
                    self.show_tip("Nothing happened")
            elif self.open_pwd_gate:
                self.typed_pwd = ""

        elif event.type == pg.KEYDOWN:
            if self.open_pwd_gate:
                if event.unicode == "\b":
                    self.typed_pwd = self.typed_pwd[:-1]
                    name = "pwd_input" + str(len(self.typed_pwd))
                    self.view(name, name + ".png")
                    play_sound("input")
                    return True
                elif len(event.unicode) == 1 and event.unicode in "0123456789":
                    self.typed_pwd += event.unicode

                    if len(self.typed_pwd) >= 8:
                        if self.typed_pwd == self.pwd_correct:
                            self.open_pwd_gate = -1
                            self.goto("end")
                            play_sound("cemetery_gate_success")
                        else:
                            self.typed_pwd = ""
                            self.show_tip("Incorrect Password", 100, (255, 0, 0))
                            play_sound("cemetery_gate_failure")
                    else:
                        name = "pwd_input" + str(len(self.typed_pwd))
                        self.view(name, name + ".png")
                        play_sound("input")
                        return True
                else:
                    self.typed_pwd = ""
                                        
    def plot_draw2(self):
        if self.showghosttime:
            self.screen.blit(self.ghost, self.ghostrect)
            self.showghosttime += 1
            if self.showghosttime > 40:
                self.quit_scene()

    def CheckTheBody(self):
        if self.check_the_body != -1:
            self.check_the_body = True

    def OpenPwdGate(self):
        if self.open_pwd_gate != -1:
            self.open_pwd_gate = True
            
    def BadEnding(self):
        self.switch_bgm("ending_bad")
        self.the_end = True

        self.result = "End"
        self.result_args = ("The End", (255, 0, 0, 50), (255, 0, 0))
        
        self.other_sprites.add(Ghost(6000,  self.main_char.rect.y-40))

    def GoodEnding(self):
        self.mm.play(MAINBGM)
        self.result = "End"
        self.result_args = ("The End", (255, 255, 255, 50), (175, 175, 175))
        self.fade_out()
        self.quit_scene()
        
class Game(Scene, Plot):
    def __init__(self, level, main_char, **kw):
        self.level = level
        self.main_char = main_char

        Plot.__init__(self)
        Scene.__init__(self, **kw)
        
    def init(self):
        self.result = "Quit"
        self.mm = MusicManager()

        self.tile_sprites = pg.sprite.Group()
        self.picked_sprites = pg.sprite.Group()
        self.obj_sprites = pg.sprite.Group()
        self.other_sprites = pg.sprite.Group()
        self.effect_sprites = pg.sprite.Group()
        self.gotos = []
        self.talks = []

        self.background = None
        self.background_size = None
        
        self.health_bar = pg.Surface((self.main_char.health_max, 20)).convert_alpha()
        self.take_damage(0)
        self.camera = vec(0, 0)
        
        self.visibility_canvas = pg.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.visibility_bubble = NoneSurf()
        self.vb_state = 1

        self.thundering = 0
        self.last_thunder = 0
        self._update_thunder_delta()

        self.tip = [None, None]
        self.tip_rect = None
        
        self.clicked = None
        self.item_key_funcs = [eval("item_functions."+func) for func in dir(item_functions) if func.startswith("key_") ]

        self.viewer = None
        self.load_map()

    def data_clear(self):
        self.tile_sprites.empty()

    def data_load(self, mapdata=None):
        if not mapdata:
            mapdata = util_pygame.load_pygame(path(f"levels/{self.level}/map.tmx"))
        for x, y, surf in self._getlayer(mapdata, "tile", tile=True):
            self.tile_sprites.add(Static(x*TILESIZE, y*TILESIZE, surf, pgim=True))
    
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
        if self.the_end: #Plot BadEnding
            self.thunder_delta = 2000
        else:
            self.thunder_delta = random.randrange(20000, 35000)

    def load_map(self):
        mapdata = util_pygame.load_pygame(path(f"levels/{self.level}/map.tmx"))
        self.show_vb = self.show_vb_default = getattr(mapdata, "show_vb", True)
        
        self.config = json.load(open(path(f"levels/{self.level}/config.json")))
        if self.config["background"].get("from"):
            bgpath = self.config["background"]["from"]
        else:
            bgpath = self.level
        self.background = pg.image.load(path(f"levels/{bgpath}/bg.png")).convert()
        self.hide = self._getlayer(mapdata, "hide")

        obj = self._getlayer(mapdata, "main_char")[0]
        self.main_char.movepos((obj.x, obj.y))
        self.main_char.game = self

        self.data_load(mapdata)
        
        for obj in self._getlayer(mapdata, "picked"):
            sprite = StaticObject(obj, floated=[(0, 0, 0), (-5, 5, 1), 60])
            sprite.picked = True
            self.picked_sprites.add(sprite)
            
        for obj in self._getlayer(mapdata, "object"):
            if hasattr(obj, "dynamic"):
                self.obj_sprites.add(DynamicObject(obj))
            else:
                self.obj_sprites.add(StaticObject(obj))

        for obj in self._getlayer(mapdata, "goto"):
            self.gotos.append((obj.x, obj.y, obj.width, obj.height, obj.goto))

        for obj in self._getlayer(mapdata, "talk"):
            self.talks.append((obj.x, obj.y, obj.width, obj.height, obj.msg))
            
        self.map_size = (mapdata.width*TILESIZE, mapdata.height*TILESIZE)
        self.background_size = self.background.get_rect().size

    def show_tip(self, text, time=100, color=(255, 255, 255)):
        if (time == 1 and self.tip[1]) or (not text): # time==1 means it's a low-level tip
            return
        
        if ":" in text:
            cdt, text = text.split(":")
            if not eval(cdt):
                return
            
        tip = render(text, color=color)
        self.tip = [tip, time]
        self.tip_rect = tip.get_rect(center=(WIDTH//2, 200))

    def not_has_tip(self, *names):
        if self.viewer:
            if any([self.viewer[2] == name for name in names]):
                return False
        return True

    def switch_bgm(self, name="ghost_scream"):
        self.mm.stop()
        play_sound(name)
        
    def doitem(self, thing, count=1):
        if count > 0:
            if hasattr(item_functions, thing):
                func = eval("item_functions."+thing)
            else:
                func = lambda *args:...
                func.__doc__ = get_name(thing)
                setattr(item_functions, thing, func)
                
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

    def take_damage(self, damage):
        self.main_char.health -= damage
        self.health_bar.fill((0, 0, 0, 0))
        pg.draw.rect(self.health_bar, (255, 0, 0), (0, 0, self.main_char.health, 10))
        pg.draw.rect(self.health_bar, (255, 255, 255), (0, 0, self.main_char.health_max, 10), width=1)

        if self.main_char.health > self.main_char.health_max:
            self.main_char.health = self.main_char.health_max
        elif self.main_char.health <= 0:
            self.main_char.alive = False
            self.show_lose_screen()
    
    def show_lose_screen(self):
        self.result = LoseScene(self).result
        self.quit_scene()

    def view(self, name, image):
        image = load_image(image)
        self.viewer = image, image.get_rect(center=(WIDTH//2, HEIGHT//2)), name

    def goto(self, place):
        self.result = place
        self.quit_scene()
                
    @property
    def package(self):
        return self.main_char.package

    def make_thunder(self):
        self._update_thunder_delta()
        self.last_thunder = pg.time.get_ticks()
        self.thundering = 1
        play_sound("thunder")
            
    def onexit(self, result="Quit"):
        self.result = result
        self.mm.stop()
        self.fade_out()
        self.quit_scene()
        
    def events(self, event):    
        self.main_char.events(event)
        view = self.plot_event(event)
        
        if event.type == pg.KEYDOWN:
            if not view:
                self.viewer = None
            
            if event.key == pg.K_SPACE and self.obj_col:
                for obj in self.obj_col:
                    obj.kspace(self)
            else:
                for func in self.item_key_funcs:
                    func(self, event.key)
            
        elif event.type == pg.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.viewer:
                    self.viewer = None
                else:
                    self.clicked = event.pos
        
    def draw(self, show_vb=True):
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
        if self.show_vb and show_vb:
            vbrect = self.visibility_bubble.get_rect(center=self.main_char.rect.center)
            pos = vbrect.topleft-self.camera
            self.visibility_canvas.fill((0, 0, 0))
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
        for i, (thing, (count, icon, func)) in enumerate(self.package.copy().items(), start=1):
            pos = WIDTH - i*70

            if count:
                self.screen.blit(icon, (pos, 30))
                self.screen.blit(render("x"+str(count), size=15), (pos+30, 50))
                if pg.Rect(pos, 30, 45, 45).collidepoint(self.pos):
                    self.show_tip(func.__doc__, 2)
                        
                    if self.clicked:
                        self.clicked = None
                        play_sound("click")
                        func(self)

        # HEALTH BAR
        self.screen.blit(self.health_bar, (30, 30))
        
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
                
        self.show_vb = self.show_vb_default
        if now - self.last_thunder > self.thunder_delta:
            self.make_thunder()
        if self.thundering:
            if self.thundering % 5 != 0:
                self.show_vb = not self.show_vb_default
                
            self.thundering += 1
            if self.thundering > 30:
                self.thundering = 0

        vbsize = int(self.main_char.torch_life*6)+120
        self.visibility_bubble = load_image(f"visibility_bubble.png", (vbsize, vbsize))

        self.obj_col = pg.sprite.spritecollide(self.main_char, self.obj_sprites, False)[::-1] # show the newest
        for obj in self.obj_col:
            if obj.enter(self):
                break

        for x, y, w, h, goto in self.gotos:
            if self.main_char.rect.colliderect(pg.Rect((x, y, w, h))):
                self.goto(goto)

        for c in self.talks:
            x, y, w, h, msg = c
            if self.main_char.rect.colliderect(pg.Rect((x, y, w, h))):
                Talk(self.draw, self, msg)
                self.talks.remove(c)

        self.effect_sprites.update()

class LoseScene(Scene):
    def __init__(self, game):
        game.mm.stop()
        play_sound("player_died")
        
        self.gdraw = game.draw
        super().__init__()

    def init(self):
        self.result = "Quit"
        
        self.background = pg.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.background.fill((255, 0, 0, 150))
        self.msg = renders([["You died", (255, 0, 0), 25],
                            ["Press <Spacebar> to retry", (255, 255, 255), 19]], pady=50)
        self.msg_pos = self.msg.get_rect(center=(WIDTH//2, HEIGHT//2)).topleft

    def quit_scene(self):
        self.fade_out()
        self.scene_running = False
        
    def events(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                self.result = "Retry"
                self.quit_scene()
                
    def draw(self):
        self.gdraw()
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.msg, self.msg_pos)
    
class EndScene(Scene):
    def __init__(self, args):
        super().__init__(loop=False)

        self.background = pg.Surface((WIDTH, HEIGHT)).convert_alpha()
        self.background.fill(args[1])
        
        self.image = render(args[0], args[2])
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT//2))
        
        self.wait_event()
        self.onexit()

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.image, self.rect)

    def onexit(self):
        self.fade_out()
        self.quit_scene()
        
class CreditsScene(Scene):
    def init(self):
        self.group = []
        self.speed = 3

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

class Loading(Scene):
    def __init__(self):
        super().__init__(caption=APPNAME, icon=load_image("icon.ico"))
        
    def init(self):
        self.background = load_image("background.png")
        self.background.blit(load_image("logo.png"), load_image("logo.png").get_rect(centerx=WIDTH//2, y=130)) 
        
        self.idx = 0
        self.assets = os.listdir(path("assets"))
        self.count = len(self.assets)
        
        pg.time.set_timer(pg.USEREVENT, 250)
        self.events(pg.Event(pg.USEREVENT))
        
    def onexit(self):
        sys.exit()
        
    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.prog, self.prog_rect)

    def events(self, event):
        if event.type == pg.USEREVENT:
            prog = self.idx / self.count
            self.prog = render("Loading " + str(int(prog * 100)) + "% ", size=18)
            self.prog_rect = self.prog.get_rect(center=(WIDTH//2, HEIGHT//2+100))
            
    def update(self):
        asset = self.assets[self.idx]
        if asset.endswith(".png"):
            load_image(asset)
        elif asset.endswith(".ogg"):
            load_sound("assets/" + asset)

        self.idx += 1
        if self.idx >= self.count:
            pg.time.set_timer(pg.USEREVENT, 0)
            self.quit_scene()

class Menu(Scene):
    def init(self):
        self.background = load_image("background.png")
        vsurf = render("Version: "+VERSION, (120, 120, 120), 14)
        self.background.blit(vsurf, vsurf.get_rect(bottomright=(WIDTH, HEIGHT)))
        
        self.click = (0, 0)
        buttons = ("Play", "Credits", "Exit")
        
        self.group = pg.sprite.Group()
        for i, text in enumerate(buttons):
            self.group.add(Button((WIDTH//2, 360+i*50), text, eval(f"self.{text}")))

        MusicManager().play(MAINBGM)
        
    def events(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.click = pg.mouse.get_pos()
            play_sound("click")

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.group.draw(self.screen)

    def update(self):
        self.group.update(pg.mouse.get_pos(), self.click)
        
    def Play(self):
        self.click = (0, 0)
        pg.mixer.music.fadeout(1000)
        self.fade_out()

        retry = True
        while retry:
            retry = self.rungame()

    def rungame(self):
        main_char = MainChar(0, 0, 100)
        gameloaded = {}
        g = Game("0", main_char, loop=False)
        g.doitem("firewood", 5)
        g.doitem("health_potion", 1)

        g.doitem("shovel", 1)
        g.doitem("rusty_key", 1)
        g.doitem("gold_key", 1)
        g.doitem("silver_key", 1)
        main_char.speed = 30
        g.doitem("bronze_key", 1) # Test
        g.loop()

        saved = None
        while True:
            if g.result == "Quit":
                return
            elif g.result == "End":
                EndScene(g.result_args)
                CreditsScene()
                return
            elif g.result == "Retry":
                if saved:
                    gameloaded = saved[0].copy()
                    main_char.update_info(saved[1])
                    main_char.alive = True
                    loaded = tuple(gameloaded.values())[-1]
                else:
                    return True
            else:
                loaded = gameloaded.get(g.result)
                gameloaded[g.level] = (g, main_char.rect.midbottom)
            saved = gameloaded.copy(), main_char.info
            if loaded:
                g.data_clear()
                last_thunder = g.last_thunder
                
                g = loaded[0]
                main_char.movepos(loaded[1])
                main_char.game = g

                g.take_damage(0)
                g.show_tip(" ", 2)
                g.thundering = 0
                g.last_thunder = last_thunder
                g._update_thunder_delta()

                delattr(g, "result")
                g.data_load()
                g.loop()
                
            else:
                g = Game(g.result, main_char)

    def Credits(self):
        self.click = (0, 0)
        self.fade_out()
        CreditsScene()

    def Exit(self):
        self.fade_out(50)
        exit()
    
if __name__ == "__main__":
    pg.init()
    pg.display.set_mode((WIDTH, HEIGHT), pg.SCALED)
    Menu()
