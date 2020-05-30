import unittest
import questgame.game_items.traps as traps
from tests.helpers.mock_helpers import MockHelper
from mock import Mock, PropertyMock

class TestTraps(unittest.TestCase):
    
    def setUp(self):
        self.trap = traps.SpikeTrap()

    def test_is_armed(self):
        #Trap armed on creation
        self.assertTrue(self.trap.is_armed)

    def test_min_damage(self):
        self.assertGreater(self.trap.min_damage, 0)

    def test_max_damage(self):
        self.assertGreater(self.trap.max_damage, 0)
        self.assertGreater(self.trap.max_damage, self.trap.min_damage)

    def test_critical_hit_multiplier(self):
        self.assertEqual(self.trap.critical_hit_multiplier, 1)

    def test_reset(self):
        self.assertTrue(self.trap.is_armed)
        self.trap.reset()
        self.assertTrue(self.trap.is_armed)

        player = Mock()
        player.get_defense = Mock(return_value=10)
        self.trap.trigger(player)
        self.assertFalse(self.trap.is_armed)
        self.trap.reset()
        self.assertTrue(self.trap.is_armed)

    def test_attack_bonus(self):
        self.assertEqual(self.trap.attack_bonus, 3)

    def test_disarm(self):
        player = Mock()
        self.assertTrue(self.trap.is_armed)
        self.trap.disarm(player)
        self.assertFalse(self.trap.is_armed)

    def test_trigger(self):
        player = Mock()
        
        #Miss
        player.get_defense = Mock(return_value=1)
        strike_result = self.trap.trigger(player)
        self.assertTrue(strike_result.is_hit)

        player.get_defense = Mock(return_value=20)
        #trap not reset
        self.assertFalse(self.trap.trigger(player))

        #Hit
        self.trap.reset()
        strike_result = self.trap.trigger(player)
        self.assertFalse(strike_result.is_hit)
