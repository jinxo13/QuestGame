import unittest
import questgame.game_items.items as items
from questgame.common.rules import Effects, Size
from mock import Mock, PropertyMock, MagicMock
from tests.helpers.mock_helpers import MockHelper

class TestItem(unittest.TestCase):
    
    def test_affect(self):
        beer = items.Beer()
        
        #Damage, Repair or nothing

        #Damage
        beer.damage = Mock()
        source = Mock()
        self.assertTrue(beer.affect(source, Effects.Damage, 10))
        beer.damage.assert_called_once()

        #Repair
        beer.repair = Mock()
        source = Mock()
        self.assertTrue(beer.affect(source, Effects.Repair, 10))
        beer.repair.assert_called_once()

        #Nothing
        source = Mock()
        self.assertFalse(beer.affect(source, None, 10))

    def test_armor_class(self):
        beer = items.Beer()
        self.assertNotEqual(beer.armor_class, 0)

    def test_class_name(self):
        beer = items.Beer()
        self.assertEqual(beer.class_name, beer.__class__.__name__)

    def test_count(self):
        beer = items.Beer()
        self.assertEqual(beer.count, 1)

        beer.count += 1
        self.assertEqual(beer.count, 2)

        beer.count -= 3
        self.assertEqual(beer.count, 0)

    def test_create_from_state(self):
        #Create
        beer = items.Beer()
        beer.count = 2
        beer_copy = items.Beer.create_from_state(beer.get_state())
        self.assertEqual(beer_copy.count, 2)
        self.assertEqual(beer_copy.__class__, items.Beer)

    def test_damage(self):
        #Break an item
        berry = items.NightBerry()
        self.assertEqual(berry.is_fragile, True)
        self.assertEqual(berry.size, Size.Small)
        self.assertEqual(berry.count, 1)
        self.assertEqual(berry.hit_points, items.ItemStats._HIT_POINTS[Size.Small][0])
        self.assertEqual(berry.max_hit_points, items.ItemStats._HIT_POINTS[Size.Small][0])
        berry.damage(1)
        self.assertEqual(berry.count, 1)
        self.assertEqual(berry.max_hit_points, items.ItemStats._HIT_POINTS[Size.Small][0])
        self.assertLess(berry.hit_points, berry.max_hit_points)
        
        #Ruin berry
        berry.damage(10)
        self.assertEqual(berry.count, 0)
        self.assertEqual(berry.hit_points, berry.max_hit_points)

    def test_description(self):
        beer = items.Beer()
        self.assertEqual(beer.description, 'beer')

    def test_description_plural(self):
        beer = items.Beer()
        self.assertEqual(beer.description_plural, 'beers')

    def test_drink(self):
        #Test eating food reduces the number of food items
        player = Mock()
        beer = items.Beer()
        beer.count = 1
        
        #Must be carrying
        #Can't be 0 items
        #Calls _effect

        #All ok
        player.is_carrying = PropertyMock(return_value=True)
        beer._effect = Mock(return_value=True)
        self.assertTrue(beer.drink(player))
        player.is_carrying.assert_called_once()
        beer._effect.assert_called_once_with('drink', player)
        self.assertEqual(0, beer.count)

        #Not carrying
        player.is_carrying = PropertyMock(return_value=False)
        beer.count = 1
        beer._effect = Mock(return_value=True)
        self.assertFalse(beer.drink(player))
        beer._effect.assert_not_called()
        self.assertEqual(1, beer.count)

        #Not enough items
        player.is_carrying = PropertyMock(return_value=True)
        beer.count = 0
        beer._effect = Mock(return_value=True)
        self.assertFalse(beer.drink(player))
        beer._effect.assert_not_called()
        self.assertEqual(0, beer.count)

    def test_get_state(self):
        #just check count is persisted
        beer = items.Beer()
        beer.count = 3
        state = beer.get_state()
        
        another_beer = items.Beer.create_from_state(state)
        self.assertEqual(another_beer.count, 3)

    def test_hit_points(self):
        beer = items.Beer()
        self.assertGreater(beer.hit_points, 0)

    def test_is_fragile(self):
        #Fragile
        beer = items.Beer()
        self.assertTrue(beer.is_fragile)

        #Not fragile
        lockpick = items.LockPick()
        self.assertFalse(lockpick.is_fragile)

    def test_is_match(self):
        beer = items.Beer()
        self.assertTrue(beer.is_match('beer'))
        self.assertTrue(beer.is_match('a beer'))

        lockpick = items.LockPick()
        self.assertTrue(lockpick.is_match('Lock Pick'))
        self.assertTrue(lockpick.is_match('lockpick'))
        self.assertTrue(lockpick.is_match('a lockpick'))

    def test_max_hit_points(self):
        beer = items.Beer()
        self.assertEqual(beer.size, items.Size.Small)
        self.assertEqual(beer.max_hit_points, 3)

    def test_name(self):
        beer = items.Beer()
        self.assertEqual(beer.name, beer.__class__.__name__)

    def test_one_of(self):
        beer = items.Beer()
        beer.count = 0
        
        #Create a single beer
        a_beer = beer.one_of()
        self.assertEqual(beer.count, 0)
        self.assertEqual(a_beer.count, 1)

    def test_repair(self):
        berry = items.NightBerry()
        berry.damage(1)
        self.assertLess(berry.hit_points, berry.max_hit_points)
        self.assertEqual(berry.count, 1)
        berry.repair(1)
        self.assertEqual(berry.hit_points, berry.max_hit_points)
        self.assertEqual(berry.count, 1)
        berry.repair(10)
        self.assertEqual(berry.hit_points, berry.max_hit_points)
        self.assertEqual(berry.count, 1)

    def test_single_weight(self):
        beer = items.Beer()
        beer.count = 1
        self.assertEqual(beer.weight, 0.1)
        self.assertEqual(beer.single_weight, 0.1)

        beer.count = 2
        self.assertEqual(beer.weight, 0.2)
        self.assertEqual(beer.single_weight, 0.1)
    
    def test_size(self):
        beer = items.Beer()
        self.assertEqual(beer.size, items.Size.Small)

    def test_text_prefix(self):
        beer = items.Beer()
        self.assertEqual(beer.text_prefix, 'a')

    def test_weight(self):
        beer = items.Beer()
        single_weight = beer.weight
        self.assertEqual(single_weight, 0.1)

        #Test add and remove and weight
        self.assertEqual(0.1, beer.weight)
        beer.count += 1
        self.assertEqual(0.2, beer.weight)

    def test_eat(self):
        #Test eating food reduces the number of food items
        player = Mock()
        bread = items.StaleBread()
        bread.count = 1
        
        #Must be carrying
        #Can't be 0 items
        #Calls _effect

        #All ok
        player.is_carrying = PropertyMock(return_value=True)
        bread._effect = Mock(return_value=True)
        self.assertTrue(bread.eat(player))
        player.is_carrying.assert_called_once()
        bread._effect.assert_called_once_with('eat', player)
        self.assertEqual(0, bread.count)

        #Not carrying
        player.is_carrying = PropertyMock(return_value=False)
        bread.count = 1
        bread._effect = Mock(return_value=True)
        self.assertFalse(bread.eat(player))
        bread._effect.assert_not_called()
        self.assertEqual(1, bread.count)

        #Not enough items
        player.is_carrying = PropertyMock(return_value=True)
        bread.count = 0
        bread._effect = Mock(return_value=True)
        self.assertFalse(bread.eat(player))
        bread._effect.assert_not_called()
        self.assertEqual(0, bread.count)

    def test_eat_bread_effect(self):
        #Test this calls Heal effect
        player = Mock()
        player.health = 100
        bread = items.StaleBread()
        bread.count = 1
        player.is_carrying = PropertyMock(return_value=True)
        player.affect = Mock()
        self.assertTrue(bread.eat(player))
        player.affect.assert_called()
        self.assertEqual(player.affect.call_args[0][1], items.Effects.Heal)

    def test_eat_bad_berry_effect(self):
        #Test this calls Damage effect
        player = Mock()
        player.health = 100
        berry = items.NightBerry()
        berry.count = 1
        player.is_carrying = PropertyMock(return_value=True)
        player.affect = Mock()
        self.assertTrue(berry.eat(player))
        player.affect.assert_called()
        self.assertEqual(player.affect.call_args[0][1], items.Effects.Damage)
