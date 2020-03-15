import random
import unittest

class Dice(object):
    """Implements dice rolling"""
    
    @staticmethod
    def roll(die=1,sides=6):
        return sum(random.randint(1, sides) for x in range(die))
