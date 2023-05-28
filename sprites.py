import pygame as pg
import os
from functools import lru_cache
from configs import *
from functions import *
from objects import *

class Button(pg.sprite.Sprite):
    def __init__(self, center, text, callback):
        super().__init__()

        self.text = text
        self.image = render(self.text)
        self.rect = self.image.get_rect(center=center)
        self.hover = False
        self.callback = callback

    def update(self, pos, click):
        if self.rect.collidepoint(pos):
            if not self.hover:
                play_sound("hover")
                self.image = render(self.text, color=(255, 0, 0))
                self.hover = True
            if pos == click:
                self.callback()
        else:
            if self.hover:
                self.image = render(self.text)
                self.hover = False
        
class Dynamic(pg.sprite.Sprite):
    def __init__(self, x, y, imgs, state=None, frame_delta=100, kill_after_play=False,
                 mark=None, call_after_kill=None):
        super().__init__()

        self.imgs = {k:load_images(v) for k, v in imgs.items()}
        self.frame_delta = frame_delta
        self.lasttime = 0
        self.played = 0
        self.state = None
        self.kill_after_play = kill_after_play
        self.call_after_kill = call_after_kill
        self.mark = mark
        self.init_special_image()

        if self.mark:
            setattr(*self.mark, 1)
            
        if state is None:
            self.cstate(tuple(self.imgs.keys())[0], x, y)
        else:
            self.cstate(state, x, y)

    def init_special_image(self):
        self.HIDE = pg.Surface((1, 1)).convert_alpha()
        self.HIDE.fill((0, 0, 0, 0))
    
    def animate(self, flip=None):
        if self.state == "HIDE":
            self.image = self.HIDE
            return
        
        now = pg.time.get_ticks()
        if now - self.lasttime > self.frame_delta:
            self.lasttime = now

            self.image = self.imgs[self.state][self.anmidx]
            if flip:
                self.image = pg.transform.flip(self.image, *flip)

            if self.mark and  (not hasattr(*self.mark)):
                self.kill()
                
            self.anmidx += 1
            if self.anmidx == len(self.imgs[self.state]):
                self.anmidx = 0
                if self.kill_after_play:
                    self.played += 1
                    if self.played == self.kill_after_play:
                        if self.mark:
                            delattr(*self.mark)
                        if self.call_after_kill:
                            self.call_after_kill(self)
                        self.kill()
            
    def cstate(self, state, x=None, y=None):
        if state != self.state:
            self.state = state
            self.anmidx = 0
    
            if x != None and y != None:
                self.animate()
                self.rect = self.image.get_rect(x=x, y=y)

class Static(pg.sprite.Sprite):
    def __init__(self, x, y, img, floated=False, pgim=False):
        super().__init__()

        if pgim:
            self.image = img
        else:
            self.image = load_image(img)
            
        self.rect = self.image.get_rect(x=x, y=y)
        
        self.floated = [seq_floated(*a) for a in floated[:-1]] + [floated[-1]] if floated else floated
        self.lasttime = 0

    def update(self):
        if self.floated:
            now = pg.time.get_ticks()
            if now - self.lasttime > self.floated[2]:
                self.lasttime = now

                self.rect.x += set_threshold(next(self.floated[0]), -1, 1)
                self.rect.y += set_threshold(next(self.floated[1]), -1, 1)

class BaseObject:
    def __init__(self):
        try:
            self.name = getattr(self.obj, "class")
        except AttributeError as e:
            raise Warning("Mark 'class' in tmx!") from e
        
        try:
            self.object_function = getattr(object_functions, self.name)
        except:
            self.object_function = lambda *args:...

        try:
            self.event = object_events[self.name]
        except:
            self.event = {}

        self.picked = False

    def c_necess(self, game):
        if self.event.get("necess"):
            return all([game.hasitem(k, v) for k, v in self.event["necess"].items()])
        return True

    def sleep(self):
        '''Keep the image but doesn't work'''
        self.event = {}
        self.picked = False
        
    def kspace(self, game):
        if self.picked:
            play_sound("picked")
            game.doitem(self.name, 1)
            self.kill()
            return
        
        if self.c_necess(game):
            if self.event.get("success"):
                try:
                    play_sound(self.name+"_success")
                except:
                    pass
                game.show_tip(*self.event["success"][0])
                
                for args in self.event["success"][1:]:
                    args = list(args)
                    for i, arg in enumerate(args):
                        if arg[0] == ".":
                            attr, default = arg[1:].split(";")
                            args[i] = getattr(self.obj, attr, eval(default))
                        
                    if args[0] == "doitem":
                        game.doitem(*args[1:])
                    elif args[0] == "view":
                        game.view(*args[1:])
                    elif args[0] == "goto":
                        game.result = args[1]
                        game.quit_scene()
            self.object_function(game, self)
                
        elif self.event.get("failure"):
            try:
                play_sound(self.name+"_failure")
            except:
                pass
            game.show_tip(*self.event["failure"])

    def enter(self, game):
        if self.event.get("enter"):
            game.show_tip(*self.event["enter"], 1)
            return True
            
class StaticObject(BaseObject, Static):
    def __init__(self, obj, **kw):
        self.obj = obj

        BaseObject.__init__(self)
        Static.__init__(self, obj.x, obj.y, obj.image, pgim=True, **kw)

class DynamicObject(BaseObject, Dynamic):
    def __init__(self, obj):
        self.obj = obj

        BaseObject.__init__(self)
        Dynamic.__init__(self, obj.x, obj.y, eval(obj.imgs), frame_delta=obj.frame_delta)

class MainChar(Dynamic):
    def __init__(self, x, y, torch_life):
        super().__init__(x, y, {"stand":"main_char_stand.png",
                                "run":"main_char_run{}.png",
                                "jump_up":"main_char_jump_up.png",
                                "jump_down":"main_char_jump_down.png"})
        self.game = None
        self.flip = False
        self.gravity = 0
        self.canjump = False
        self.last_height = 0
        self.torch = Dynamic(0, 0, {"":"torch{}.png"})
        self.torch_life = torch_life
        self.package = {}

        self.alive = True
        self.health_max = 100
        self.health = self.health_max
        
        self.speed = 4
        self.jump_velocity = 25
        self.height_max = 280
        
    @property
    def info(self):
        return self.health, self.torch_life, self.package

    def update_info(self, info):
        self.health, self.torch_life, self.package = info
    
    def movepos(self, pos):
        self.rect.midbottom = pos
        self.last_height = pos[1]
        
    def jump(self):
        if self.canjump:
            self.cstate("jump_up")
            self.canjump = False
            self.gravity = -self.jump_velocity

    def jump_over(self):
        if not self.canjump:
            self.gravity *= 0.33

    def check_height(self):
        falling = self.rect.bottom - self.last_height
        self.last_height = self.rect.bottom
        
        if falling > self.height_max:
            play_sound("player_fall")
            damage = falling//12
            self.game.take_damage(damage)
            self.game.show_tip("Ouch! You fell from a high place", 100, (255, 0, 0))

    def draw(self):
        if self.alive:
            pos = self.rect.topleft-self.game.camera
            if pos[1] > HEIGHT:
                self.health = 0
                self.game.take_damage(0)
            else:
                self.game.screen.blit(self.image, pos)

                self.torch.animate()
                self.game.screen.blit(self.torch.image, self.torch.rect.topleft-self.game.camera)
            
    def events(self, event):
        if event.type == pg.KEYDOWN and event.key == pg.K_UP:
            self.jump()
        elif event.type == pg.KEYDOWN and event.key == pg.K_UP:
            self.jump_over()
            
    def update(self):
        self.animate(flip=(self.flip, False))
            
        if self.gravity >= 0:
            self.gravity += 1
            if self.gravity > 9:
                self.gravity = 9
        elif self.gravity < 0:
            self.gravity += 1.1
            if self.gravity == 0:
                self.gravity = 0.7
                
        keys = pg.key.get_pressed()
        move = [0, self.gravity]

        if keys[pg.K_LEFT]:
            self.flip = True
            move[0] = -self.speed
            self.cstate("run")
                
        elif keys[pg.K_RIGHT]:
            self.flip = False
            move[0] = self.speed
            self.cstate("run")
        else:
            self.cstate("stand")

        self.rect.x += move[0]
        collision = pg.sprite.spritecollide(self, self.game.tile_sprites, False)
        if collision:
            for tile in collision:
                if move[0] > 0:
                    self.rect.right = tile.rect.left
                elif move[0] < 0:
                    self.rect.left = tile.rect.right

        self.rect.y += move[1]
        collision = pg.sprite.spritecollide(self, self.game.tile_sprites, False)
        if collision:
            for tile in collision:
                if move[1] > 0:
                    self.rect.bottom = tile.rect.top
                    self.canjump = True
                    self.check_height()
                elif move[1] < 0:
                    self.rect.top = tile.rect.bottom
                    self.gravity = 0
        else:
            if self.gravity > 0:
                self.cstate("jump_down")
                self.canjump = False
            elif self.gravity < 0:
                self.cstate("jump_up")
                self.canjump = False

        if move[0] == 0:
            if self.flip:
                self.torch.rect.x = self.rect.left + 3
            else:
                self.torch.rect.x = self.rect.right - 8
        else:
            if self.flip:
                self.torch.rect.x = self.rect.left - 5
            else:
                self.torch.rect.x = self.rect.right
        self.torch.rect.bottom = self.rect.centery - 5

        self.torch_life -= 0.02
        if self.torch_life <= 0:
            self.torch_life = 0
            self.torch.cstate("HIDE")
        else:
            self.torch.cstate("")

class Ghost(Dynamic):
    def __init__(self, x, y):
        super().__init__(x, y, {"":"ghost_move{}.png"})

        self.isscreaming = False

    def update(self, game):
        self.animate()
            
        if game.main_char.rect.x > self.rect.x:
            self.rect.x += 10
        else:
            if not game.showghosttime:
                game.viewer = None
                game.showghosttime = 1

        if self.rect.x - game.camera.x > 0 and not self.isscreaming:
            play_sound("ghost_scream")
            self.isscreaming = True

@lru_cache()
def NoneSurf(size=(1, 1)):
    surf = pg.Surface(size).convert_alpha()
    surf.fill((0, 0, 0, 0))

    return surf
