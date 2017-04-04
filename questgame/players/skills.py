from questgame.common.dice import Dice
from questgame.common.rules import ATTRIBUTES

class Skill(object):
    """description of class"""
    def __init__(self): pass

class AttackSkill(Skill):
    """description of class"""
    def __init__(self): super(AttackSkill, self).__init__()
    @property
    def attribute_modifier(self): return ATTRIBUTES.DEXTERITY
    def damage(self, player):
        if not player.character_class.is_skill_proficient(player, self):
            #Shouldn't be able to happen
            return 0
        dmg_dice = player.character_class.get_skill_damage(self, player.level)
        dmg = Dice.roll_dice(dmg_dice[0],dmg_dice[1])
        mod = player.get_equipped_weapon().get_modifier_value(self.__class__)
        return dmg + mod

class Stealth(Skill): pass
class SneakAttack(AttackSkill): pass
