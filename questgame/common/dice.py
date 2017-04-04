import random

class Dice(object):
    """Implements dice rolling"""
    
    @staticmethod
    def roll_dice(die=1,sides=6):
        result = 0
        for i in range(0,die):
            result = result + random.randint(1, sides)
        return result
