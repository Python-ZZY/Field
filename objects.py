import random
from configs import *

object_events = {
    "dec":{},
    "cemetery_gate":{
        "enter":("Press <Spacebar> to enter",),
        "necess":{"bronze_key":1, "gold_key":1, "rusty_key":1, "silver_key":1},
        "failure":("You need 4 keys to unlock the gate!", 100, (255, 0, 0)),
        "success":(("",), ("goto", ".goto;'1'")) #tip, commands(. means it needs attr in tmx)
        },
    "pwd_gate":{
        "enter":("Press <Spacebar> to enter",),
        "success":(("",), ("view", "pwd_gate", "pwd_input0.png")),
        },
    "dead_tree":{
        "enter":("Press <Spacebar> to look for firewood",)
        },
    "tomb_g_e":{
        "enter":("self.not_has_tip('letter'):Press <Spacebar> to view",),
        "success":(("self.not_has_tip('tomb_g_e'):",), ("view", "tomb_g_e", "tomb_g_e.png")),
        },
    "tomb_place_of_death":{
        "enter":("Press <Spacebar> to view",),
        "success":(("self.not_has_tip('tomb_place_of_death'):",),
                   ("view", "tomb_place_of_death", "tomb_place_of_death.png")),
        },
    "skeleton_sitting":{
        "enter":("self.not_has_tip('skeleton_s'):Press <Spacebar> to check the body",),
        "success":(("",), ("view", "skeleton_s", "skeleton_s_b.png")),
        },
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
            game.doitem("firewood")
            game.show_tip("You found some firewood", color=(255, 0, 0))
            if rand > 0.95:
                game.show_tip("The tree was destroyed", color=(255, 0, 0)) 
                game.play_effect(obj.rect.midbottom, "tree_fire{}.png")
                obj.kill()
        else:
            game.show_tip("You found nothing")

    @staticmethod
    def skeleton_sitting(game, obj):
        game.CheckTheBody()

    @staticmethod
    def pwd_gate(game, obj):
        game.OpenPwdGate()
