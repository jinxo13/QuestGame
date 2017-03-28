import unittest
from players.players import Player
from common.rules import GameRules, ATTRIBUTES
from common.dice import Dice
from common.utils import Helpers
from players import skills, character_classes
from game_items import weapons, armor

class test_stats(unittest.TestCase):
    def test_Dice(self):
        self.assertTrue(Helpers.is_number(Dice.roll_dice()))
        self.assertNotEquals(0,Dice.roll_dice())

    def test_GameRules(self):
        self.assertEqual(-5,GameRules.get_attribute_modifier(0))
        self.assertEqual(-5,GameRules.get_attribute_modifier(1))
        self.assertEqual(1,GameRules.get_attribute_modifier(12))
        self.assertEqual(1,GameRules.get_attribute_modifier(13))
        self.assertEqual(2,GameRules.get_attribute_modifier(14))
        self.assertEqual(2,GameRules.get_attribute_modifier(15))
        self.assertEqual(10,GameRules.get_attribute_modifier(30))
        self.assertEqual(10,GameRules.get_attribute_modifier(31))

    """
    1. Adding named modifier replaces existing modifer
    2. Supports multiple modifiers for an attribute
    """
    def test_PlayerModifiers(self):
        player = Player(character_classes.Thief)

        self.assertEqual(player.strength_base,0)
        player.strength_base = 9
        self.assertEqual(player.strength_base,9)

        player.add_modifier('SPOTION',ATTRIBUTES.STRENGTH, 2)
        self.assertEqual(player.strength_base,9)
        self.assertEqual(player.strength,11)

        player.add_modifier('SSPELL',ATTRIBUTES.STRENGTH, 3)
        self.assertEqual(player.strength,14)

        player.add_modifier('SPOTION',ATTRIBUTES.STRENGTH, 4)
        self.assertEqual(player.strength,16)

        player.remove_modifier('SSPELL')
        self.assertEqual(player.strength,13)

        player.remove_modifier('XXX')
        self.assertEqual(player.strength,13)

        player.strength_base = 11
        self.assertEqual(player.strength_base,11)
        self.assertEqual(player.strength,15)

        #Test armor adjustments
        player.dexterity_base = 12
        self.assertEqual(player.dexterity_base,12)
        self.assertEqual(player.dexterity,12)
        player.equip_armor(armor.HeavyArmor()) #-2 dexterity penalty
        self.assertEqual(player.dexterity_base,12)
        self.assertEqual(player.dexterity,10)
        #Test weapon adjustments
        player.equip_weapon(weapons.ThiefsDagger()) #+2 dexterity penalty
        self.assertEqual(player.dexterity_base,12)
        self.assertEqual(player.dexterity,12,"Thiefs dagger adjustment")
        player.equip_armor(armor.BodyArmor())
        self.assertEqual(player.dexterity_base,12)
        self.assertEqual(player.dexterity,14)
        player.equip_weapon(weapons.Fists())
        self.assertEqual(player.dexterity_base,12)
        self.assertEqual(player.dexterity,12)

    def test_RulesLevel(self):
        player = Player(character_classes.Thief)
        self.assertEqual(1,player.level)
        player.add_experience(400)
        self.assertEqual(2,player.level)
        player.add_experience(32000)
        self.assertEqual(7,player.level)
        self.assertEqual(3,player.proficiency)

    def test_Weapon(self):
        player = Player(character_classes.Thief())
        player.strength_base = 17
        player.equip_weapon(weapons.Dagger())
        player.level = 2
        self.assertEqual(2,player.get_weapon_proficiency())
        player.equip_weapon(weapons.LongBow())
        self.assertEqual(0,player.get_weapon_proficiency())

        player.level = 5
        player.equip_weapon(weapons.Dagger())
        self.assertEqual(3,player.get_weapon_proficiency())
        player.equip_weapon(weapons.LongBow())
        self.assertEqual(0,player.get_weapon_proficiency())

        #Test damage
        player.strength_base = 17 #+3 modifier
        player.equip_weapon(weapons.Dagger()) #1D6

        self.assertTrue(player.get_equipped_weapon().is_critical_strike(20))
        self.assertFalse(player.get_equipped_weapon().is_critical_strike(21))
        self.assertFalse(player.get_equipped_weapon().is_critical_strike(19))

        for i in range(100):
            dmg = player.get_equipped_weapon()._normal_strike(player) #1D6
            print "Player Weapon Damage: {}".format(dmg)
            self.assertGreaterEqual(dmg, 4)
            self.assertLessEqual(dmg, 9)
        #Critical strike
        for i in range(100):
            dmg = player.get_equipped_weapon()._critical_strike(player) #1D6 + 1D6 + 3*2
            print "Player Weapon Damage: {}".format(dmg)
            self.assertGreaterEqual(dmg, 8)
            self.assertLessEqual(dmg, 18)

    def test_Armor(self):
        player = Player(character_classes.Thief())
        player.strength_base = 17
        player.level = 2
        self.assertEqual(5,player.get_armor_class())
        player.dexterity_base = 17
        self.assertEqual(13,player.get_armor_class())
        player.equip_armor(armor.LightArmor())
        self.assertEqual(14,player.get_armor_class())
        player.add_modifier('POTION',ATTRIBUTES.DEXTERITY, 4)
        self.assertEqual(16,player.get_armor_class())

    def test_Skills(self):
        player = Player(character_classes.Thief())
        player.strength_base = 17
        player.equip_weapon(weapons.Dagger())
        player.level = 5 #3d6 damage
        for i in range(100):
            dmg = skills.SneakAttack().damage(player)
            print "Player Sneak Attack score: {}".format(dmg)
            self.assertGreaterEqual(dmg, 3)
            self.assertLessEqual(dmg, 18)

        #Add ThiefsDagger (+1 SneakAttack bonus)
        player.equip_weapon(weapons.ThiefsDagger())
        for i in range(100):
            dmg = skills.SneakAttack().damage(player)
            print "Player Sneak Attack score: {}".format(dmg)
            self.assertGreaterEqual(dmg, 4)
            self.assertLessEqual(dmg, 19)


    def test_Attack(self):
        player = Player(character_classes.Thief())
        player.strength_base = 17 #+3 strength modifier
        player.equip_weapon(weapons.Dagger()) #+2 proficiency
        for i in range(100):
            dice_roll, atk = GameRules.roll_weapon_attack_score(player) #5 - 25
            critical_strike = player.get_equipped_weapon().is_critical_strike(dice_roll)
            atk = dice_roll + atk
            print "Player Attack score: {}".format(atk)
            self.assertGreaterEqual(atk, 5)
            self.assertLessEqual(atk, 25)

        player.add_modifier('POTION',ATTRIBUTES.STRENGTH, 4) #21 strength, +5 strength modifer
        for i in range(100):
            dice_roll, atk = GameRules.roll_weapon_attack_score(player)
            critical_strike = player.get_equipped_weapon().is_critical_strike(dice_roll)
            atk = dice_roll + atk
            print "Player Attack score: {}".format(atk)
            self.assertGreaterEqual(atk, 7)
            self.assertLessEqual(atk, 27)

        player.remove_modifier('POTION')
        player.equip_weapon(weapons.LongBow()) #0 proficiency
        player.dexterity_base = 0 #-5 dexterity modifier
        for i in range(100):
            dice_roll, atk = GameRules.roll_weapon_attack_score(player)
            critical_strike = player.get_equipped_weapon().is_critical_strike(dice_roll)
            atk = dice_roll + atk
            print "Player Attack score: {}".format(atk)
            self.assertGreaterEqual(atk, -4)
            self.assertLessEqual(atk, 15)
        
        player.dexterity_base = 12 #+1 dexterity modifier
        for i in range(100):
            dice_roll, atk = GameRules.roll_weapon_attack_score(player)
            critical_strike = player.get_equipped_weapon().is_critical_strike(dice_roll)
            atk = dice_roll + atk
            print "Player Attack score: {}".format(atk)
            self.assertGreaterEqual(atk, 2)
            self.assertLessEqual(atk, 21)


if __name__ == '__main__':
    unittest.main()
