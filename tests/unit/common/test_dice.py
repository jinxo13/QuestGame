import unittest
from questgame.common.dice import Dice

class TestDice(unittest.TestCase):
    def __test_roll(self, rolls, die, sides):
        do_roll = (Dice.roll(die,sides) for x in range(rolls))
        result = {}

        #Test dice values are in the expected range
        for roll in do_roll:
            result[roll] = 1
            self.assertGreaterEqual(roll, die*1, 'Minimum roll. Die: %i, Sides: %i' % (die, sides))
            self.assertLessEqual(roll, sides*die, 'Maximum roll. Die: %i, Sides: %i' % (die, sides))
        
        #Test every possible value has at least one entry
        for val in range(die, die*sides+1):
           self.assertTrue(val in result.keys(), 'Possible dice result exists, failed to find %i' % val)

    def test_roll(self):
        rolls = 1000
        #1 x 6 sided die
        self.__test_roll(rolls, 1, 6)
        #2 x 6 sided die
        self.__test_roll(rolls, 2, 6)
        #1 x 12 sided die
        self.__test_roll(rolls, 1, 12)
        
        rolls = 50000
        #6 x 12 sided die
        self.__test_roll(rolls, 3, 12)
