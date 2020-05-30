import unittest
from questgame.players.players import Thief
from questgame.common.rules import GameRules, PlayerAttributes
from questgame.common.dice import Dice
from questgame.common.utils import Helpers
from questgame.players import skills, character_classes
from questgame.game_items import weapons, armor

class test_stats(unittest.TestCase):

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
        player = Thief()

        player.strength_base = 9
        self.assertEqual(player.strength_base,9)

        player.add_bonus('SPOTION',PlayerAttributes.STRENGTH, 2)
        self.assertEqual(player.strength_base,9)
        self.assertEqual(player.strength,11)

        player.add_bonus('SSPELL',PlayerAttributes.STRENGTH, 3)
        self.assertEqual(player.strength,14)

        player.add_bonus('SPOTION',PlayerAttributes.STRENGTH, 4)
        self.assertEqual(player.strength,16)

        player.remove_bonus('SSPELL')
        self.assertEqual(player.strength,13)

        player.remove_bonus('XXX')
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
        player = Thief()
        self.assertEqual(1,player.level)
        player.add_experience(400)
        self.assertEqual(2,player.level)
        player.add_experience(32000)
        self.assertEqual(7,player.level)
        self.assertEqual(3,player.proficiency_bonus)

    def test_Weapon(self):
        player = Thief()
        player.strength_base = 17
        player.equip_weapon(weapons.Dagger())

        player.add_experience(14000)
        self.assertEqual(player.level, 5)
        player.equip_weapon(weapons.Dagger())
        self.assertEqual(3,player.determine_ability_modifier())
        player.equip_weapon(weapons.LongBow())
        self.assertEqual(0,player.determine_ability_modifier())

        #Test damage
        player.strength_base = 17 #+3 modifier
        player.equip_weapon(weapons.Dagger()) #1D6

        self.assertTrue(player.get_equipped_weapon().is_critical_strike(20))
        self.assertFalse(player.get_equipped_weapon().is_critical_strike(21))
        self.assertFalse(player.get_equipped_weapon().is_critical_strike(19))

        for _i in range(100):
            dmg = player.get_equipped_weapon()._normal_strike(player) #1D6
            print("Player Weapon Damage: {}".format(dmg))
            self.assertGreaterEqual(dmg, 4)
            self.assertLessEqual(dmg, 9)
        #Critical strike
        for _i in range(100):
            dmg = player.get_equipped_weapon()._critical_strike(player) #1D6 + 1D6 + 3*2
            print("Player Weapon Damage: {}".format(dmg))
            self.assertGreaterEqual(dmg, 8)
            self.assertLessEqual(dmg, 18)

    def test_Skills(self):
        player = Thief()
        player.strength_base = 17
        player.equip_weapon(weapons.Dagger())
        player.add_experience(14000)
        self.assertEqual(player.level, 5) #3d6 damage
        for _i in range(100):
            dmg = skills.SneakAttack().damage(player)
            print("Player Sneak Attack score: {}".format(dmg))
            self.assertGreaterEqual(dmg, 3)
            self.assertLessEqual(dmg, 18)

        #Add ThiefsDagger (+1 SneakAttack bonus)
        player.equip_weapon(weapons.ThiefsDagger())
        for _i in range(100):
            dmg = skills.SneakAttack().damage(player)
            print("Player Sneak Attack score: {}".format(dmg))
            self.assertGreaterEqual(dmg, 4)
            self.assertLessEqual(dmg, 19)


    def test_Attack(self):
        player = Thief() #+2 attack bonus at level 1
        player.strength_base = 17 #+3 strength modifier
        player.equip_weapon(weapons.Dagger()) #+2 proficiency
        for _i in range(100):
            dice_roll = GameRules.roll_weapon_attack_score(player)
            #critical_strike = player.get_equipped_weapon().is_critical_strike(dice_roll.roll)
            print("Player Attack score: {}".format(dice_roll.total))
            if not player.get_equipped_weapon().is_critical_miss(dice_roll.roll):
                self.assertGreaterEqual(dice_roll.total, 7)
            self.assertLessEqual(dice_roll.total, 27)

        player.add_bonus('POTION',PlayerAttributes.STRENGTH, 4) #21 strength, +5 strength modifer
        for _i in range(100):
            dice_roll = GameRules.roll_weapon_attack_score(player)
            #critical_strike = player.get_equipped_weapon().is_critical_strike(dice_roll.roll)
            print("Player Attack score: {}".format(dice_roll.total))
            if not player.get_equipped_weapon().is_critical_miss(dice_roll.roll):
                self.assertGreaterEqual(dice_roll.total, 9)
            self.assertLessEqual(dice_roll.total, 29)

        player.remove_bonus('POTION')
        player.equip_weapon(weapons.LongBow()) #0 proficiency
        player.dexterity_base = 0 #-5 dexterity modifier, +2 attack bonus
        for _i in range(100):
            dice_roll = GameRules.roll_weapon_attack_score(player)
            #critical_strike = player.get_equipped_weapon().is_critical_strike(dice_roll.roll)
            print("Player Attack score: {}".format(dice_roll.total))
            if not player.get_equipped_weapon().is_critical_miss(dice_roll.roll):
                self.assertGreaterEqual(dice_roll.total, -2)
            self.assertLessEqual(dice_roll.total, 17)
        
        player.dexterity_base = 12 #+1 dexterity modifier
        for _i in range(100):
            dice_roll = GameRules.roll_weapon_attack_score(player)
            #critical_strike = player.get_equipped_weapon().is_critical_strike(dice_roll.total)
            print("Player Attack score: {}".format(dice_roll.total))
            if not player.get_equipped_weapon().is_critical_miss(dice_roll.roll):
                self.assertGreaterEqual(dice_roll.total, 4)
            self.assertLessEqual(dice_roll.total, 23)


if __name__ == '__main__':
    unittest.main()
