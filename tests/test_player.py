import unittest
from game_items import weapons, armor, items, spells, traps, potions
from game_items.standard_items import Inventory, Chest
from players import character_classes, players
from common import base_classes
from common.utils import Helpers
from common.rules import GameRules

class Test_Others(unittest.TestCase):
    
    def test_potions(self):
        player = players.Player(character_classes.Thief())
        base_classes.Observer(player)

        healing_potion = potions.HealingPotion()
        harm_potion = potions.HarmPotion()
        strength_potion = potions.StrengthPotion()

        player.pickup(healing_potion)
        player.pickup(harm_potion)
        player.pickup(strength_potion)

        player.max_hit_points = 100
        player.wound(20)
        player.drink_potion(healing_potion)
        self.assertGreater(player.hit_points, 80)

        player.heal(20)
        player.drink_potion(harm_potion)
        self.assertLess(player.hit_points, 100)

        player.strength_base = 10
        self.assertEqual(player.strength, 10)
        player.drink_potion(strength_potion)
        self.assertEqual(player.strength, 12)

    def test_encumbered(self):
        player = players.Player(character_classes.Thief())
        goblin = players.Goblin()
        base_classes.Observer(player)
        base_classes.Observer(goblin)
        player.strength_base = 1
        player.dexterity_base = 5
        goblin.strength_base = 1

        rocks = Helpers.create_instances(weapons.Rock, 8)

        self.assertEqual(player.carry_capacity, 15)
        self.assertEqual(player.carry_weight, 0)
        player.pickup(rocks[0])
        self.assertEqual(player.carry_weight, 2)
        player.pickup(rocks[1])
        player.pickup(rocks[2])
        player.pickup(rocks[3])
        player.pickup(rocks[4])
        player.pickup(rocks[5])
        player.pickup(rocks[6])
        self.assertEqual(player.carry_weight, 14)
        self.assertEqual(player.is_encumbered, False)
        self.assertEqual(player.dexterity,5)
        player.pickup(rocks[7])
        self.assertEqual(player.is_encumbered, True)
        self.assertEqual(player.dexterity,1) #4 point penalty
        player.drop(rocks[7])
        self.assertEqual(player.is_encumbered, False)
        self.assertEqual(player.dexterity,5)

        player.give(rocks[0],goblin)
        player.give(rocks[1],goblin)
        player.give(rocks[2],goblin)
        player.give(rocks[3],goblin)
        player.give(rocks[4],goblin)
        player.give(rocks[5],goblin)
        player.give(rocks[6],goblin)

        player.pickup(rocks[7])
        self.assertEqual(goblin.carry_weight, 14)
        self.assertEqual(goblin.is_encumbered, False)
        player.give(rocks[7],goblin)
        self.assertEqual(goblin.is_encumbered, True)
        goblin.drop(rocks[7])
        self.assertEqual(goblin.is_encumbered, False)

    def test_pickup(self):
        player = players.Player(character_classes.Thief())
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
        player = players.Player(character_classes.Thief())
        player.equip_weapon(weapons.Dagger())
        player.equip_armor(armor.LightArmor())
        player.strength_base = 8
        player.dexterity_base = 10
        player.intelligence_base = 9
        player.max_hit_points = 100
        player.level = 1
        heal_spell = spells.HealSpell()
        harm_spell = spells.HarmSpell()
        
        a = base_classes.Observer(player)
        player.wound(12)
        player.cast(heal_spell, player)
        self.assertEqual(player.hit_points, 98)
        player.cast(heal_spell, player)
        self.assertEqual(player.hit_points, 100)
        
        player.cast(harm_spell, player)
        player.cast(harm_spell, player)
        player.cast(harm_spell, player)
        player.cast(harm_spell, player)
        player.cast(harm_spell, player)
        self.assertNotEqual(player.hit_points, 100)

        save_throw = player.get_attribute_modifier(harm_spell.saving_throw_attribute)
        player.constitution_base = 0
        self.assertEqual(save_throw, -5)
        

    def test_chest_actions(self):
        player = players.Player(character_classes.Thief())
        player.equip_weapon(weapons.Dagger())
        player.equip_armor(armor.LightArmor())
        player.strength_base = 8
        player.dexterity_base = 10
        player.intelligence_base = 9
        player.max_hit_points = 100
        open_spell = spells.OpenSpell()
        close_spell = spells.CloseSpell()
        unlock_spell = spells.UnlockSpell()
        lock_spell = spells.LockSpell()
        good_key = items.Key(1)
        bad_key =  items.Key(2)

        chest = Chest(1)
        
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
        player = players.Player(character_classes.Thief())
        player.equip_weapon(weapons.Dagger())
        player.equip_armor(armor.LightArmor())
        player.strength_base = 8
        player.dexterity_base = 10
        player.intelligence_base = 15
        player.max_hit_points = 100
        spell = spells.FireballSpell()

        goblin = players.Goblin()
        goblin.max_hit_points = 100
        a = base_classes.Observer(goblin)
        b = base_classes.Observer(player)

        while not goblin.is_dead:
            player.cast(spell, goblin)

        goblin = players.Goblin()
        player.intelligence_base = 18
        goblin.max_hit_points = 100
        a = base_classes.Observer(goblin)
        player.level = 2
        while not goblin.is_dead:
            player.cast(spell, goblin)


    def test_traps(self):
        player = players.Player(character_classes.Thief())
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
            print "SpikeTrap caused {} damage".format(dmg)
            player.heal(dmg)
            spikeTrap.reset()
        self.assertTrue(dmg_occured)

        dmg_occured = False
        player.level = 1
        for i in range(100):
            self.assertTrue(spellTrap.is_armed)
            dmg = spellTrap.trigger(player)
            if dmg>0: dmg_occured = True
            self.assertGreaterEqual(dmg, 0)
            self.assertLessEqual(dmg, 6) #max damage
            self.assertEqual(player.hit_points, 100 - dmg)
            self.assertFalse(spellTrap.is_armed)
            print "SpellTrap caused {} damage".format(dmg)
            player.heal(dmg)
            spellTrap.reset()
        self.assertTrue(dmg_occured)

        dmg_occured = False
        player.level = 3
        for i in range(100):
            self.assertTrue(spellTrap.is_armed)
            dmg = spellTrap.trigger(player)
            if dmg>0: dmg_occured = True
            self.assertGreaterEqual(dmg, 0)
            self.assertLessEqual(dmg, 18) #max damage
            self.assertEqual(dmg / 3, dmg // 3)
            self.assertEqual(player.hit_points, 100 - dmg)
            self.assertFalse(spellTrap.is_armed)
            print "SpellTrap caused {} damage".format(dmg)
            player.heal(dmg)
            spellTrap.reset()
        self.assertTrue(dmg_occured)

    def test_inventory(self):
        player = players.Player(character_classes.Thief())
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
        self.assertEqual(0,inv.count_items(a.__class__)) 
        inv.add(a)
        self.assertEqual(a.weight,inv.weight)
        self.assertEqual(1,inv.count) 
        self.assertEqual(1,inv.count_items(a.__class__)) 
        #add second item
        inv.add(b)
        self.assertEqual(a.weight+b.weight,inv.weight)
        self.assertEqual(2,inv.count) 
        self.assertEqual(1,inv.count_items(a.__class__)) 
        self.assertEqual(1,inv.count_items(b.__class__)) 

        #add same item
        inv.add(b)
        self.assertEqual(a.weight+b.weight,inv.weight)
        self.assertEqual(2,inv.count) 
        self.assertEqual(1,inv.count_items(a.__class__)) 
        self.assertEqual(1,inv.count_items(b.__class__)) 

        #remove first item
        inv.remove(a)
        self.assertEqual(b.weight,inv.weight)
        self.assertEqual(1,inv.count) 
        self.assertEqual(0,inv.count_items(a.__class__)) 
        self.assertEqual(1,inv.count_items(b.__class__)) 

        #remove second item
        inv.remove(b)
        self.assertEqual(0,inv.weight)
        self.assertEqual(0,inv.count) 
        self.assertEqual(0,inv.count_items(a.__class__)) 
        self.assertEqual(0,inv.count_items(b.__class__)) 

        #remove item not in inventory
        inv.remove(c)
        self.assertEqual(0,inv.weight)
        self.assertEqual(0,inv.count) 
        self.assertEqual(0,inv.count_items(a.__class__)) 
        self.assertEqual(0,inv.count_items(b.__class__)) 
        self.assertEqual(0,inv.count_items(c.__class__))

        #Test getting arrows
        f = inv.find_ammo(weapons.Arrow)
        self.assertIsNone(f)
        inv.add(weapons.WoodArrow())
        inv.add(weapons.IronArrow())
        inv.add(weapons.SteelArrow())
        inv.add(weapons.WoodArrow())
        f = inv.find_ammo(weapons.Arrow)
        self.assertEqual(f[0].__class__, weapons.SteelArrow)

if __name__ == '__main__':
    unittest.main()
