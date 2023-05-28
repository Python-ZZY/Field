import pygame as pg

def checkhasitem(func):
    def function(game, key):
        if game.hasitem(func.__name__.lstrip("key_")):
            func(game, key)
            
    return function

def viewer(func):
    name = func.__name__
    
    def function(game):
        game.view(name, name+"_view.png")

    doc = function.__doc__
    function.__doc__ = doc if doc else f"self.not_has_tip({repr(name)}):Click to view"
    
    return function
        
def _shovel_cak(sprite):
    game = sprite.mark[0]
    for obj in game.hide:
        col = sprite.rect.colliderect(pg.Rect(obj.x, obj.y, obj.width, obj.height))
        if col:
            game.show_tip("You dug up something and put it into the package", color=(255, 0, 0))
            game.doitem(getattr(obj, "class"))
            game.hide.remove(obj)
            return
    game.show_tip("You dug up nothing")

class item_functions:
    '''Use function.__doc__ to show tip about the item'''
    
    @staticmethod
    def firewood(game):
        """Click to light the torch"""
        game.main_char.torch_life = 100
        game.doitem("firewood", -1)

    @staticmethod
    def health_potion(game):
        """Restores 10% health points"""
        game.take_damage(-10)
        game.doitem("health_potion", -1)
        
    @staticmethod
    def shovel(game):
        """Press <D> to dig"""

    @checkhasitem
    def key_shovel(game, key):
        if not hasattr(game, "isdigging") and \
           key == pg.K_d and \
           game.main_char.state in ("stand", "run"):
            game.show_tip("Digging... Don't move!", 200)
            game.play_effect(game.main_char.rect.midbottom, "dig{}.png",
                             kill_after_play=10, mark=(game, "isdigging"),
                             call_after_kill=_shovel_cak)

    @viewer
    def parchment_1():
        pass

    @viewer
    def parchment_2():
        pass

    @viewer
    def parchment_3():
        pass
    
    @viewer
    def parchment_pwd():
        pass
    
    @viewer
    def skeleton_drawing():
        pass

    @staticmethod
    def letter(game):
        """self.not_has_tip('letter'):Click to view"""
        game.view("letter", "letter_view.png")
        game.BadEnding()
        
    @staticmethod
    def update(game):
        if hasattr(game, "isdigging"):
            if game.main_char.state != "stand":
                delattr(game, "isdigging")
                game.show_tip(" ", 2)
    
