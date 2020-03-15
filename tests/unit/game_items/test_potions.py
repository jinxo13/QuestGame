import unittest
import questgame.game_items.potions as potions
from questgame.common.rules import Effects
from tests.helpers.mock_helpers import MockHelper
from mock import Mock, PropertyMock

class TestPotions(unittest.TestCase):
    
    def test_drink(self):
        #is carrying
        #has 1 left

        #Not carrying
        potion = potions.StrengthPotion()
        self.assertEqual(potion.count, 1)
        player = Mock()
        mock_is_carrying = PropertyMock(return_value=False)
        player.is_carrying = mock_is_carrying
        self.assertFalse(potion.drink(player))
        mock_is_carrying.assert_called_once()
        self.assertEqual(potion.count, 1)

        #Carrying
        mock_is_carrying.return_value = True
        self.assertTrue(potion.drink(player))
        self.assertEqual(potion.count, 0)

        #None left
        self.assertFalse(potion.drink(player))
