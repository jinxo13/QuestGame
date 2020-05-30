import unittest
import json
from questgame.game_items import weapons, armor, items, spells, traps, potions
from questgame.game_items.standard_items import Inventory
from questgame.rooms.room import Chest, CellRoom
from questgame.players import character_classes, players
from questgame.common import base_classes
from questgame.common.utils import Helpers
from questgame.common.rules import GameRules

class TestItems(unittest.TestCase):

    def test_pickup(self):
        beer = items.Beer()
        bread = items.StaleBread()

        thief = players.Thief()
        self.assertTrue(thief.pickup(beer))
        self.assertTrue(thief.pickup(bread))

        state = players.Thief().get_state()
        thief = players.Player.create_from_state(state)
        
        self.assertTrue(thief.is_carrying(bread))
        self.assertTrue(thief.is_carrying(beer))

    def test_equipped(self):
        thief = players.Thief()
        self.assertFalse(thief.has_armor_equipped())
        self.assertFalse(thief.has_weapon_equipped())
        self.assertTrue(thief.equip_armor(armor.LightArmor()))
        self.assertTrue(thief.equip_weapon(weapons.Dagger()))

        state = players.Thief().get_state()
        thief = players.Player.create_from_state(state)
        self.assertTrue(thief.has_armor_equipped())
        self.assertTrue(thief.has_weapon_equipped())


class Test_Others(unittest.TestCase):
    
    def test_potions(self):
        player = players.Thief()
        base_classes.Observer(player)

        healing_potion = potions.HealingPotion()
        harm_potion = potions.HarmPotion()
        strength_potion = potions.StrengthPotion()

        player.pickup(healing_potion)
        player.pickup(harm_potion)
        player.pickup(strength_potion)

        player.max_hit_points = 100
        player.wound(20)
        player.drink(healing_potion)
        self.assertGreater(player.hit_points, 80)

        player.heal(20)
        player.drink(harm_potion)
        self.assertLess(player.hit_points, 100)

        player.strength_base = 10
        self.assertEqual(player.strength, 10)
        player.drink(strength_potion)
        self.assertEqual(player.strength, 12)

    def test_encumbered(self):
        player = players.Thief()
        goblin = players.Goblin()
        base_classes.Observer(player)
        base_classes.Observer(goblin)
        player.strength_base = 1
        player.dexterity_base = 5
        goblin.strength_base = 1

        rocks = weapons.Rock(7)
        rock = weapons.Rock()

        self.assertEqual(player.carry_capacity, 15)
        self.assertEqual(player.carry_weight, 0)
        player.pickup(rocks)
        self.assertEqual(player.carry_weight, 14)
        self.assertEqual(player.is_encumbered, False)
        self.assertEqual(player.dexterity,5)

        player.pickup(rock)
        self.assertEqual(player.carry_weight, 16)
        self.assertEqual(player.is_encumbered, True)
        self.assertEqual(player.dexterity,1) #4 point penalty

        player.drop(rock)
        self.assertEqual(player.is_encumbered, False)
        self.assertEqual(player.dexterity,5)
        self.assertEqual(player.carry_weight, 14)

        player.give(rocks,goblin)
        self.assertEqual(goblin.carry_weight, 14)
        self.assertEqual(player.carry_weight, 0)
        self.assertEqual(goblin.is_encumbered, False)

        player.pickup(rock)
        player.give(rock,goblin)
        self.assertEqual(goblin.is_encumbered, True)
        goblin.drop(rocks)
        self.assertEqual(goblin.carry_weight, 2)
        self.assertEqual(goblin.is_encumbered, False)

    def test_pickup(self):
        player = players.Thief()
        goblin = players.Goblin()
        base_classes.Observer(player)
        base_classes.Observer(goblin)

        ring1 = items.StrengthRing()
        ring2 = items.StrengthRing()

        self.assertTrue(player.pickup(ring1))
        self.assertTrue(player.give(ring1, goblin))
        self.assertFalse(player.give(ring2, goblin))
        self.assertFalse(player.drop(ring1))
        self.assertFalse(player.drop(ring2))
        self.assertTrue(goblin.drop(ring1))

    def test_heal_spell(self):
        player = players.Mage()
        player.equip_weapon(weapons.Dagger())
        player.equip_armor(armor.LightArmor())
        player.strength_base = 8
        player.dexterity_base = 10
        player.intelligence_base = 9
        player.max_hit_points = 100
        player.add_experience(300)
        #TODO Max mana on start
        player.add_mana(player.max_mana_points)

        self.assertEqual(player.level, 2)
        heal_spell = spells.HealSpell()
        harm_spell = spells.HarmSpell()

        a = base_classes.Observer(player)
        player.wound(22)
        player.learn_spell(heal_spell)
        player.learn_spell(harm_spell)
        self.assertTrue(player.cast(heal_spell, player))
        self.assertEqual(player.hit_points, 98)
        self.assertTrue(player.cast(heal_spell, player))
        self.assertEqual(player.hit_points, 100)
        
        player.cast(harm_spell, player)
        player.cast(harm_spell, player)
        player.cast(harm_spell, player)
        player.cast(harm_spell, player)
        player.cast(harm_spell, player)
        self.assertNotEqual(player.hit_points, 100)

        save_throw = player.get_attribute_modifier(harm_spell.saving_throw_attribute)
        player.constitution_base = 0
        self.assertEqual(save_throw, 0)
        

    def test_chest_actions(self):
        player = players.Mage()
        player.equip_weapon(weapons.Dagger())
        player.equip_armor(armor.LightArmor())
        player.strength_base = 8
        player.dexterity_base = 10
        player.intelligence_base = 9
        player.max_hit_points = 100
        player.add_experience(34000)
        self.assertEqual(player.level, 7)
        open_spell = spells.OpenSpell()
        close_spell = spells.CloseSpell()
        unlock_spell = spells.UnlockSpell()
        lock_spell = spells.LockSpell()
        player.learn_spell(open_spell)
        player.learn_spell(close_spell)
        player.learn_spell(unlock_spell)
        player.learn_spell(lock_spell)
        good_key = items.CellRoomKey()
        bad_key =  items.WeaponsRoomKey()


        chest = Chest(CellRoom(player), key_id=good_key.id)
        
        a = base_classes.Observer(player)

        self.assertTrue(chest.is_locked)
        self.assertFalse(chest.is_open)
        self.assertFalse(chest.is_trapped)

        chest.open(player)
        self.assertFalse(chest.is_open)

        player.cast(open_spell, chest)
        self.assertFalse(chest.is_open)

        player.cast(close_spell, chest)
        self.assertFalse(chest.is_open)
        
        player.cast(unlock_spell, chest)
        self.assertFalse(chest.is_locked)

        player.cast(open_spell, chest)
        self.assertTrue(chest.is_open)

        player.max_mana_points = 100

        player.cast(close_spell, chest)
        self.assertFalse(chest.is_open)

        player.cast(lock_spell, chest)
        self.assertTrue(chest.is_locked)

        chest.unlock_with_key(bad_key, player)
        self.assertTrue(chest.is_locked)

        chest.unlock_with_key(good_key, player)
        self.assertFalse(chest.is_locked)

        chest.unlock_with_key(good_key, player)
        self.assertFalse(chest.is_locked)

        chest.lock_with_key(bad_key, player)
        self.assertFalse(chest.is_locked)

        chest.lock_with_key(good_key, player)
        self.assertTrue(chest.is_locked)

        chest.unlock_with_key(good_key, player)
        self.assertFalse(chest.is_locked)
        chest.lock_with_spell(lock_spell, player)
        self.assertTrue(chest.is_locked)
        chest.unlock_with_key(good_key, player)
        chest.lock_with_spell(unlock_spell, player)
        self.assertFalse(chest.is_locked)

        chest.set_trap(traps.SpikeTrap())
        chest.unlock_with_key(good_key, player)
        self.assertTrue(chest.is_trapped)
        self.assertTrue(chest.trap.is_armed)
        chest.open(player)
        self.assertTrue(chest.is_trapped)
        self.assertFalse(chest.trap.is_armed)


    def test_firespell(self):
        player = players.Mage()
        player.equip_weapon(weapons.Dagger())
        player.equip_armor(armor.LightArmor())
        player.strength_base = 8
        player.dexterity_base = 10
        player.intelligence_base = 15
        player.max_hit_points = 100
        spell = spells.FireballSpell()
        self.assertTrue(player.can_cast_spell(spells.FireballSpell()))
        self.assertFalse(player.can_cast_spell(spells.UnlockSpell()))
        goblin = players.Goblin()
        goblin.max_hit_points = 100
        a = base_classes.Observer(goblin)
        b = base_classes.Observer(player)

        while not goblin.is_dead and player.mana_points > 0:
            self.assertTrue(player.cast(spell, goblin))

    def test_traps(self):
        player = players.Thief()
        player.equip_weapon(weapons.Dagger())
        player.equip_armor(armor.LightArmor())
        player.strength_base = 15
        player.dexterity_base = 10
        player.max_hit_points = 100

        spikeTrap = traps.SpikeTrap()
        spellTrap = traps.FireballTrap()
        
        dmg_occured = False
        for i in range(100):
            self.assertTrue(spikeTrap.is_armed)
            dmg = spikeTrap.trigger(player)
            if dmg>0: dmg_occured = True
            self.assertGreaterEqual(dmg, 0)
            self.assertLessEqual(dmg, 7) #max damage
            self.assertEqual(player.hit_points, 100 - dmg)
            self.assertFalse(spikeTrap.is_armed)
            print("SpikeTrap caused {} damage".format(dmg))
            player.heal(dmg)
            spikeTrap.reset()
        self.assertTrue(dmg_occured)

        dmg_occured = False
        self.assertEqual(player.level, 1)
        for i in range(100):
            self.assertTrue(spellTrap.is_armed)
            dmg = spellTrap.trigger(player)
            if dmg>0: dmg_occured = True
            self.assertGreaterEqual(dmg, 0)
            self.assertLessEqual(dmg, 6) #max damage
            self.assertEqual(player.hit_points, 100 - dmg)
            self.assertFalse(spellTrap.is_armed)
            print("SpellTrap caused {} damage".format(dmg))
            player.heal(dmg)
            spellTrap.reset()
        self.assertTrue(dmg_occured)

        dmg_occured = False
        player.add_experience(2700)
        self.assertEqual(player.level, 3)
        for i in range(100):
            self.assertTrue(spellTrap.is_armed)
            dmg = spellTrap.trigger(player)
            if dmg>0: dmg_occured = True
            self.assertGreaterEqual(dmg, 0)
            self.assertLessEqual(dmg, 18) #max damage
            self.assertEqual(dmg / 3, dmg // 3)
            if dmg_occured:
                self.assertEqual(player.hit_points, 100 - dmg)
                player.heal(dmg)
                self.assertFalse(spellTrap.is_armed)
                print("SpellTrap caused {} damage".format(dmg))
            spellTrap.reset()

    def test_inventory(self):
        player = players.Thief()
        inv = Inventory(player)
        a = items.StrengthRing()
        b = weapons.LongBow()
        c = armor.LightArmor()

        self.assertGreater(a.weight,0)
        self.assertGreater(b.weight,0)
        self.assertGreater(c.weight,0)

        #add one item
        self.assertEqual(0,inv.weight)
        self.assertEqual(0,inv.count) 
        self.assertEqual(0,inv.count_items(a)) 
        inv.add(a)
        self.assertEqual(a.weight,inv.weight)
        self.assertEqual(1,inv.count) 
        self.assertEqual(1,inv.count_items(a)) 
        #add second item
        inv.add(b)
        self.assertEqual(a.weight+b.weight,inv.weight)
        self.assertEqual(2,inv.count) 
        self.assertEqual(1,inv.count_items(a)) 
        self.assertEqual(1,inv.count_items(b)) 

        #add same item
        inv.add(b)
        self.assertEqual(a.weight+b.weight*2,inv.weight)
        self.assertEqual(3,inv.count) 
        self.assertEqual(1,inv.count_items(a)) 
        self.assertEqual(2,inv.count_items(b)) 
        inv.remove(b)

        #remove first item
        inv.remove(a)
        self.assertEqual(b.weight,inv.weight)
        self.assertEqual(1,inv.count) 
        self.assertEqual(0,inv.count_items(a)) 
        self.assertEqual(1,inv.count_items(b)) 

        #remove second item
        inv.remove(b)
        self.assertEqual(0,inv.weight)
        self.assertEqual(0,inv.count) 
        self.assertEqual(0,inv.count_items(a)) 
        self.assertEqual(0,inv.count_items(b)) 

        #remove item not in inventory
        inv.remove(c)
        self.assertEqual(0,inv.weight)
        self.assertEqual(0,inv.count) 
        self.assertEqual(0,inv.count_items(a)) 
        self.assertEqual(0,inv.count_items(b)) 
        self.assertEqual(0,inv.count_items(c))

        #Test getting arrows
        self.assertFalse(inv.find_ammo(weapons.Arrow))
        inv.add(weapons.WoodArrow())
        inv.add(weapons.IronArrow())
        inv.add(weapons.SteelArrow())
        inv.add(weapons.WoodArrow())
        f = inv.find_ammo(weapons.Arrow)
        self.assertEqual(f.__class__, weapons.SteelArrow)

        #Test keys
        key = items.CellRoomKey()
        self.assertFalse(inv.contains(key))
        inv.add(key)
        self.assertTrue(inv.contains(key))
        self.assertTrue(inv.contains(items.CellRoomKey()))

        #Test Money
        for itm in inv.items():
            inv.remove(itm)
        self.assertEqual(0,inv.count)
        gold = items.Gold(4)
        silver = items.Silver(3)
        copper = items.Copper(6)
        inv.add(gold)
        inv.add(silver)
        inv.add(copper)
        self.assertEqual(round(13 * 0.001,3), inv.weight)
        self.assertEqual(13,inv.count)
        self.assertEqual(4.36,inv.money)

        silver = items.Silver(16)
        inv.add(silver)
        gold = inv.get_item(items.Gold())
        self.assertEqual(5,gold.count)
        self.assertEqual(9,inv.get_item(items.Silver()).count)
        self.assertEqual(6,inv.get_item(items.Copper()).count)
        self.assertEqual(round(20 * 0.001,3),inv.weight)
        self.assertEqual(20,inv.count)

        copper = items.Copper(23)
        inv.add(copper)
        self.assertEqual(6,inv.get_item(items.Gold()).count)
        self.assertEqual(1,inv.get_item(items.Silver()).count)
        self.assertEqual(9,inv.get_item(items.Copper()).count)
        self.assertEqual(round(16 * 0.001,3),inv.weight)
        self.assertEqual(16,inv.count)

        for itm in inv.items():
            inv.remove(itm)
        inv.add_money(10.51)
        self.assertEqual(10,inv.get_item(items.Gold()).count)
        self.assertEqual(5,inv.get_item(items.Silver()).count)
        self.assertEqual(1,inv.get_item(items.Copper()).count)

        inv.remove_money(9.88)
        self.assertFalse(inv.get_item(items.Gold()))
        self.assertEqual(6,inv.get_item(items.Silver()).count)
        self.assertEqual(3,inv.get_item(items.Copper()).count)

if __name__ == '__main__':
    unittest.main()
