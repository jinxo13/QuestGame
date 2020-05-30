from questgame.common.dice import Dice
from questgame.common.rules import PlayerAttributes

class Skill(object):
    """description of class"""
    def __init__(self): pass

class DextrousSkill(Skill):
    @property
    def attribute_modifier(self): return PlayerAttributes.DEXTERITY

class DextrousAttackSkill(DextrousSkill):
    """description of class"""
    def __init__(self): super(DextrousAttackSkill, self).__init__()
    def damage(self, player):
        if not player.character_class.is_skill_proficient(player, self):
            #Shouldn't be able to happen
            return 0
        dmg_dice = player.character_class.get_skill_damage(self, player.level)
        dmg = Dice.roll(dmg_dice[0],dmg_dice[1])
        #TODO is this right?
        mod = player.get_attribute_modifier([self.attribute_modifier])
        return dmg + mod

class StrengthAttackSkill(DextrousAttackSkill):
    @property
    def attribute_modifier(self): return PlayerAttributes.STRENGTH

class Stealth(DextrousSkill): pass
class LockPicking(DextrousSkill): pass
class SneakAttack(DextrousAttackSkill): pass
class CriticalShot(DextrousAttackSkill): pass
class Berserker(StrengthAttackSkill): pass
