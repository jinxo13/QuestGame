import unittest
import questgame.game_items.items as items
from questgame.common.rules import Effects, Size
from mock import Mock, PropertyMock

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

    def test_create_from_state(self): return self.assertFalse(True)
    def test_damage(self):
        #Break an item
        berry = items.NightBerry()
        self.assertEqual(berry.is_fragile(), True)
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

    def test_description(self): return self.assertFalse(True)
    def test_description_plural(self): return self.assertFalse(True)
    def test_drink(self): return self.assertFalse(True)
    def test_get_state(self): return self.assertFalse(True)
    def test_hit_points(self): return self.assertFalse(True)
    def test_is_fragile(self): return self.assertFalse(True)
    def test_is_match(self): return self.assertFalse(True)
    def test_max_hit_points(self): return self.assertFalse(True)
    def test_name(self): return self.assertFalse(True)
    def test_one_of(self): return self.assertFalse(True)
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

    def test_single_weight(self): return self.assertFalse(True)
    def test_size(self): return self.assertFalse(True)
    def test_text_prefix(self): return self.assertFalse(True)
    def test_throw_strike(self): return self.assertFalse(True)
    def test_weight(self):
        beer = items.Beer()
        single_weight = beer.weight
        self.assertEqual(single_weight, 0.1)

        #Test add and remove and weight
        self.assertEqual(0.1, beer.weight)
        beer.count += 1
        self.assertEqual(0.2, beer.weight)

    def test_bread(self):
        #Test eating food reduces the number of food items
        player = Mock()
        bread = items.StaleBread()
        bread.eat(player)
        self.assertEqual(0, bread.count, 'Ate some bread')
        #Test eating good food increases health
        self.assertEqual(player.health, 100 + items.ItemStats.get_heal_amount(bread))
        self.assertTrue(player.health > 100)

    def test_bad_berry(self):
        #Test eating bad food decreases health
        player = Mock()
        berry = items.NightBerry()
        berry.eat(player)
        self.assertEqual(player.health, 100 + items.ItemStats.get_heal_amount(berry))
        self.assertTrue(player.health < 100)
