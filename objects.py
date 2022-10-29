import random
from configs import *

object_events = {
    "dec":{},
    "cemetery_gate":{
        "enter":("Press <Spacebar> to enter",),
        "necess":{"bronze_key":1, "gold_key":1, "rusty_key":1, "silver_key":1},
        "failure":("You need 4 keys to unlock the gate!", 100, (255, 0, 0)),
        "success":(("",), ("goto", "1")) #tip, commands
        },
    "dead_tree":{
        "enter":("Press <Spacebar> to look for firewood",)
        },
    "skeleton_sitting":{
        "enter":("Press <Spacebar> to check the body",),
        "success":(("You found a letter", 100, (255, 0, 0)), ("gain", "letter", 1)),
        }
    }

class object_functions:
    @staticmethod
    def dec(game, obj):
        pass
    
    @staticmethod
    def dead_tree(game, obj):
        play_sound("wood_crack")

        rand = random.random()
        if rand > 0.3:
            game.gain("firewood")
            game.show_tip("You found some firewood", color=(255, 0, 0))
            if rand > 0.9:
                game.show_tip("The tree was destroyed", color=(255, 0, 0)) 
                game.play_effect(obj.rect.midbottom, "tree_fire{}.png")
                obj.kill()
        else:
            game.show_tip("You found nothing")

    @staticmethod
    def skeleton_sitting(game, obj):
        obj.kill()

