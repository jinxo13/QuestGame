import unittest
from mock import Mock, PropertyMock
from questgame.common.rules import GameRules

class TestRules(unittest.TestCase):
    
    def test_determine_carry_capacity(self):
        player = Mock()
        player.strength = 10
        self.assertEqual(GameRules.determine_carry_capacity(player), player.strength * 15)
