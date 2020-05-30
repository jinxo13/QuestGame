import unittest
import questgame.game_items.standard_items as standard_items
from questgame.common.rules import Difficulty, Actions
from mock import Mock, PropertyMock, MagicMock
from tests.helpers.mock_helpers import MockHelper

class TestOpenableItem(unittest.TestCase):

    def test_check_trapped(self):
        player = Mock()
        trap = Mock()
        trap.difficulty_class = Difficulty.Easy

        dice = Mock()
        dice.total = 10

        standard_items.GameRules.roll_perception_check = Mock(return_value=dice)
        chest = standard_items.OpenableItem()
        self.assertTrue(chest.check_for_trap(player, trap))

        dice.total = 9
        self.assertFalse(chest.check_for_trap(player, trap))

    def test_close(self):
        player = Mock()
        chest = standard_items.OpenableItem()
        chest.on_close = Mock()
        #Chest not open or locked
        self.assertFalse(chest.is_open)
        self.assertFalse(chest.is_locked)
        self.assertFalse(chest.close(player))
        chest.on_close.assert_not_called()

        #Chest open
        self.assertTrue(chest.open(player))
        self.assertTrue(chest.is_open)
        self.assertTrue(chest.close(player))
        chest.on_close.assert_called_once()

        #Open with chest locked
        chest = standard_items.OpenableItem(key_id=1)
        chest.on_close = Mock()
        key = Mock()
        key.id = 1
        self.assertTrue(chest.is_locked)
        self.assertFalse(chest.open(player))

        #unlock
        self.assertTrue(chest.unlock(player, key))
        self.assertFalse(chest.is_locked)
        self.assertTrue(chest.open(player))

        #With spell
        spell = Mock()
        self.assertTrue(chest.is_open)
        player.current_action = Actions.CAST
        self.assertTrue(chest.close(player, spell))
        chest.on_close.assert_called_once()
        player.current_action = False

        #Trap
        trap = Mock()
        trap.trigger = Mock()
        self.assertFalse(chest.is_trapped)
        self.assertFalse(chest.is_open)
        chest.set_trap(trap)
        self.assertTrue(chest.is_trapped)

        #Trigger Trap
        self.assertTrue(chest.open(player))
        trap.trigger.assert_called_once()

    def test_get_key(self):
        key = Mock()
        chest = standard_items.OpenableItem(key_id=10)
        #Mock key lookup
        with MockHelper.Method(standard_items.items.ItemStats, 'get_key', return_value=key) as mock_get_key:
            self.assertEqual(chest.get_key(), key)
            mock_get_key.assert_called_once()

    def test_has_been_opened(self):
        player = Mock()
        chest = standard_items.OpenableItem()
        self.assertFalse(chest.has_been_opened)
        chest.open(player)
        self.assertTrue(chest.has_been_opened)

    def test_is_trapped(self):
        chest = standard_items.OpenableItem()
        self.assertFalse(chest.is_trapped)
        trap = Mock()
        chest.set_trap(trap)
        self.assertTrue(chest.is_trapped)

    def test_lock_resistance(self):
        chest = standard_items.OpenableItem()
        self.assertEqual(chest.lock_resistance, Difficulty.Easy)

    def test_lock_with_key(self):
        player = Mock()
        key = Mock()
        key.id = 1

        bad_key = Mock()
        bad_key.id = 2

        chest = standard_items.OpenableItem(key_id=1)
        self.assertTrue(chest.is_locked)
        self.assertFalse(chest.unlock(player, bad_key))
        self.assertTrue(chest.unlock(player, key))
        self.assertTrue(chest.is_unlocked)

        self.assertFalse(chest.lock(player, bad_key))
        self.assertTrue(chest.lock(player, key))
        self.assertTrue(chest.is_locked)
        
    def test_lock_with_spell(self):
        player = Mock()
        bad_spell = Mock()
        spell = MockHelper.get_mock_lock_spell()

        chest = standard_items.OpenableItem()
        self.assertFalse(chest.is_locked)
        self.assertFalse(chest.lock(player, spell=bad_spell))
        self.assertTrue(chest.lock(player, spell=spell))
        self.assertTrue(chest.is_locked)

        #Can't unlock with key
        key = Mock()
        key.id = 1
        self.assertFalse(chest.unlock(player, key))

        #Can picklock
        player.current_action = Actions.PICK_LOCK
        player.get_attribute_modifier = Mock(return_value=5)
        self.assertTrue(chest.unlock(player))
        player.get_attribute_modifier.assert_called_once()
        player.current_action = False

    def test_on_close(self):
        #Covered in close
        pass

    def test_on_lock(self):
        #Covered in lock
        pass

    def test_on_open(self):
        #Covered in open
        pass

    def test_on_unlock(self):
        #Covered in unlock
        pass

    def test_open(self):
        player = Mock()
        chest = standard_items.OpenableItem()
        chest.on_open = Mock()

        #Chest not open or locked
        self.assertFalse(chest.is_open)
        self.assertFalse(chest.is_locked)

        #Chest open
        self.assertTrue(chest.open(player))
        chest.on_open.assert_called_once()
        self.assertTrue(chest.is_open)

        #Open with chest locked
        chest = standard_items.OpenableItem(key_id=1)
        chest.on_open = Mock()
        key = Mock()
        key.id = 1
        self.assertTrue(chest.is_locked)
        self.assertFalse(chest.open(player))
        chest.on_open.assert_not_called()

        #unlock
        self.assertTrue(chest.unlock(player, key))
        self.assertFalse(chest.is_locked)
        self.assertTrue(chest.open(player))
        chest.on_open.assert_called_once()
        self.assertTrue(chest.is_open)

        #With spell
        spell = Mock()
        chest = standard_items.OpenableItem()
        chest.on_open = Mock()
        self.assertTrue(chest.is_closed)
        player.current_action = Actions.CAST
        self.assertTrue(chest.open(player, spell))
        chest.on_open.assert_called_once()
        player.current_action = False

    def test_open_with_spell(self):
        pass

    def test_set_locked(self):
        player = Mock()
        chest = standard_items.OpenableItem()

    def test_set_trap(self):
        player = Mock()
        #Trap
        trap = Mock()
        trap.trigger = Mock()
        chest = standard_items.OpenableItem()
        self.assertFalse(chest.is_trapped)
        self.assertFalse(chest.is_open)

        #Trigger Trap
        chest.set_trap(trap)
        self.assertTrue(chest.is_trapped)
        
        self.assertTrue(chest.open(player))
        trap.trigger.assert_called_once()
        
        #Check no retrigger
        self.assertTrue(chest.close(player))
        trap.trigger = Mock()
        trap.is_armed = False
        self.assertTrue(chest.open(player))
        trap.trigger.assert_not_called()
        
    def test_spell_resistance(self):
        chest = standard_items.OpenableItem()
        self.assertEqual(chest.spell_resistance, standard_items.Difficulty.Easy)

    def test_trap(self):
        trap = Mock()
        chest = standard_items.OpenableItem()
        chest.set_trap(trap)
        self.assertTrue(chest.is_trapped)
        self.assertEqual(chest.trap, trap)
        
    def test_unlock(self):
        player = Mock()
        #key
        key = Mock()
        key.id = 1
        chest = standard_items.OpenableItem(key_id=1)
        chest.on_unlock = Mock()
        self.assertTrue(chest.is_locked)
        self.assertTrue(chest.unlock(player, key))
        self.assertTrue(chest.is_unlocked)
        #chest.on_unlock.assert_called_once()

class TestInventory(unittest.TestCase):
    
    def test_add(self):
        player = Mock()
        inventory = standard_items.Inventory(player)
        
        #Add None
        self.assertFalse(inventory.add(None))

        #Add non-item
        self.assertFalse(inventory.add(Mock()))

        #Add item
        beer = MockHelper.get_mock_beer()
        self.assertTrue(inventory.add(beer))
        self.assertTrue(inventory.contains(beer))

    def test_add_money(self):
        player = Mock()
        inventory = standard_items.Inventory(player)

        #Add some money
        self.assertTrue(inventory.add_money(10))
        self.assertTrue(inventory.items() != [])
        self.assertEqual(inventory.money, 10)

    def test_contains(self):
        player = Mock()
        inventory = standard_items.Inventory(player)
        beer = MockHelper.get_mock_beer()

        self.assertFalse(inventory.contains(beer))
        self.assertTrue(inventory.add(beer))
        self.assertTrue(inventory.contains(beer))

    def test_count(self):
        player = Mock()
        inventory = standard_items.Inventory(player)
        self.assertEqual(inventory.count, 0)

    def test_count_items(self):
        player = Mock()
        beer = MockHelper.get_mock_item()

        inventory = standard_items.Inventory(player)
        #Test None
        self.assertEqual(inventory.count_items(None), 0)
        self.assertEqual(inventory.count_items(beer), 0)

        #Test 1 item
        self.assertTrue(inventory.add(beer))
        self.assertEqual(inventory.count_items(beer), 1)

        #Test 2 items
        self.assertTrue(inventory.add(beer))
        self.assertEqual(inventory.count_items(beer), 2)


    def test_find_ammo(self):
        player = Mock()
        inventory = standard_items.Inventory(player)
        import questgame.game_items.weapons as weapons
        ammo_poor = MockHelper.get_mock_item(spec=weapons.WoodArrow)
        ammo_poor.cost = 1

        ammo_best = MockHelper.get_mock_item(spec=weapons.SteelArrow)
        ammo_best.cost = 100

        ammo_good = MockHelper.get_mock_item(spec=weapons.IronArrow)
        ammo_good.cost = 10

        #Add poor arrow
        self.assertEqual(inventory.find_ammo(weapons.Arrow), False)
        inventory.add(ammo_poor)

        #Add best arrow
        self.assertEqual(inventory.find_ammo(weapons.Arrow), ammo_poor)
        inventory.add(ammo_best)
        self.assertEqual(inventory.find_ammo(weapons.Arrow), ammo_best)

        #Add good arrow - should still select best arrow
        inventory.add(ammo_good)
        self.assertEqual(inventory.find_ammo(weapons.Arrow), ammo_best)

    def test_get_item(self):
        player = Mock()
        inventory = standard_items.Inventory(player)
        beer = MockHelper.get_mock_item()
        
        #Nothing in inventroy
        self.assertFalse(inventory.get_item(beer))

        #Beer is in inventory
        self.assertTrue(inventory.add(beer))
        self.assertEqual(inventory.get_item(beer), beer)


    def test_items(self):
        player = Mock()
        inventory = standard_items.Inventory(player)

        #Nothing in inventory
        self.assertEqual(inventory.items(), [])

        beer = MockHelper.get_mock_beer()
        self.assertTrue(inventory.add(beer))
        self.assertTrue(inventory.add(MockHelper.get_mock_beer()))
        self.assertEqual(inventory.items(), [beer])
        
        scroll = MockHelper.get_mock_scroll()
        self.assertTrue(inventory.add(scroll))
        self.assertTrue(inventory.add(MockHelper.get_mock_scroll()))
        self.assertEqual(inventory.items(), [beer, scroll])

    def test_money(self):
        player = Mock()
        inventory = standard_items.Inventory(player)
        self.assertEqual(inventory.money, 0.00)

        #Add some money
        coin = MockHelper.get_mock_money()
        coin.cost = 10
        self.assertTrue(inventory.add(coin))
        self.assertEqual(inventory.money, 10.00)

        #Add some more money
        coin = MockHelper.get_mock_money()
        coin.cost = 0.05
        self.assertTrue(inventory.add(coin))
        self.assertEqual(inventory.money, 10.05)

    def test_remove(self):
        player = Mock()
        inventory = standard_items.Inventory(player)

        beer = MockHelper.get_mock_beer()
        self.assertFalse(inventory.remove(beer))

        inventory.add(beer)
        self.assertTrue(inventory.remove(beer))
        self.assertFalse(inventory.contains(beer))

    def test_remove_money(self):
        player = Mock()
        inventory = standard_items.Inventory(player)

        #Remove money we don't have
        self.assertFalse(inventory.remove_money(3))
        self.assertEqual(inventory.money, 0)

        self.assertTrue(inventory.add_money(3.5))
        self.assertEqual(inventory.money, 3.5)
        self.assertTrue(inventory.remove_money(3))
        self.assertEqual(inventory.money, 0.5)
        self.assertTrue(inventory.remove_money(1))
        self.assertEqual(inventory.money, 0)

    def test_weight(self):
        player = Mock()
        inventory = standard_items.Inventory(player)

        self.assertEqual(inventory.weight, 0)
        beer = MockHelper.get_mock_beer()
        scroll = MockHelper.get_mock_scroll()
        inventory.add(beer)
        self.assertEqual(inventory.weight, 1)
        inventory.add(beer)
        self.assertEqual(inventory.weight, 2)
        
        inventory.add(scroll)
        self.assertEqual(inventory.weight, 3)
        inventory.remove(scroll)
        self.assertEqual(inventory.weight, 2)
