import unittest
import questgame.game_items.weapons as weapons
from mock import Mock, PropertyMock
import mock
from tests.helpers.mock_helpers import MockHelper

class MockDiceRoll:
    def __init__(self, roll, modifier):
        self.roll = roll
        self.modifier = modifier
        self.total = 1 if self.roll == 1 else self.roll + self.modifier

class TestWeapons(unittest.TestCase):

    def test_strike_hit(self):
        weapon = weapons.Spear()
        attacker = Mock()
        defender = Mock()
        is_throw = False

        attacker.get_reply_key = Mock(return_value='player_strike')
        defender.get_reply_key = Mock(return_value='monster_strike')
        attacker.determine_ability_modifier = Mock(return_value=2)
        defender.get_defense = Mock(return_value=5)

        with MockHelper.Method(weapons.GameRules, 'roll_weapon_attack_score', return_value=MockDiceRoll(5,0)) as mock_weapon_roll:
            strike = weapon.strike(attacker, defender, is_throw)
            mock_weapon_roll.assert_called_once()
            self.assertFalse(strike.is_critical_hit)
            self.assertFalse(strike.is_critical_miss)
            self.assertGreater(strike.damage, 0)
            self.assertTrue(strike.is_hit)
            self.assertFalse(strike.is_miss)

    def test_strike_miss(self):
        weapon = weapons.Spear()
        attacker = Mock()
        defender = Mock()
        is_throw = False

        attacker.get_reply_key = Mock(return_value='player_miss')
        defender.get_reply_key = Mock(return_value='monster_miss')
        attacker.determine_ability_modifier = Mock(return_value=2)
        defender.get_defense = Mock(return_value=5)

        with MockHelper.Method(weapons.GameRules, 'roll_weapon_attack_score', return_value=MockDiceRoll(4,0)) as mock_weapon_roll:
            strike = weapon.strike(attacker, defender, is_throw)
            mock_weapon_roll.assert_called_once()
            self.assertFalse(strike.is_critical_hit)
            self.assertFalse(strike.is_critical_miss)
            self.assertEqual(strike.damage, 0)
            self.assertFalse(strike.is_hit)
            self.assertTrue(strike.is_miss)

    def test_strike_critical_miss(self):
        weapon = weapons.Spear()
        attacker = Mock()
        defender = Mock()
        is_throw = False

        attacker.get_reply_key = Mock(return_value='player_critical_miss')
        defender.get_reply_key = Mock(return_value='monster_critical_miss')
        attacker.determine_ability_modifier = Mock(return_value=2)
        defender.get_defense = Mock(return_value=5)

        with MockHelper.Method(weapons.GameRules, 'roll_weapon_attack_score') as mock_weapon_roll:
            mock_weapon_roll.return_value = MockDiceRoll(1,0)
            strike = weapon.strike(attacker, defender, is_throw)
            weapons.GameRules.roll_weapon_attack_score.assert_called_once()
            self.assertFalse(strike.is_critical_hit)
            self.assertTrue(strike.is_critical_miss)
            self.assertEqual(strike.damage, 0)
            self.assertFalse(strike.is_hit)
            self.assertTrue(strike.is_miss)

    def test_strike_throw(self):
        weapon = weapons.Spear()
        attacker = Mock()
        defender = Mock()
        is_throw = True

        attacker.get_reply_key = Mock(return_value='player_strike')
        defender.get_reply_key = Mock(return_value='monster_strike')
        attacker.determine_ability_modifier = Mock(return_value=2)
        defender.get_defense = Mock(return_value=5)

        with MockHelper.Method(weapons.GameRules, 'roll_weapon_throw_score') as mock_weapon_roll:
            mock_weapon_roll.return_value=MockDiceRoll(5,0)
            self.assertTrue(weapon.is_throwable)
            strike = weapon.strike(attacker, defender, is_throw)
            mock_weapon_roll.assert_called_once()
            self.assertFalse(strike.is_critical_hit)
            self.assertFalse(strike.is_critical_miss)
            self.assertGreater(strike.damage, 0)
            self.assertTrue(strike.is_hit)
            self.assertFalse(strike.is_miss)

    def test_strike_not_throwable(self):
        #Not throwable
        attacker = Mock()
        defender = Mock()
        is_throw = True
        self.assertFalse(weapons.ShortSword().strike(attacker, defender, is_throw))

    def test_strike_critical_hit(self):
        weapon = weapons.Spear()
        attacker = Mock()
        defender = Mock()
        is_throw = False

        attacker.get_reply_key = Mock(return_value='player_critical_strike')
        defender.get_reply_key = Mock(return_value='monster_critical_strike')
        attacker.determine_ability_modifier = Mock(return_value=2)
        defender.get_defense = Mock(return_value=5)
        
        with MockHelper.Method(weapons.GameRules, 'roll_weapon_attack_score') as mock_weapon_roll:
            mock_weapon_roll.return_value=MockDiceRoll(20,0)
            strike = weapon.strike(attacker, defender, is_throw)
            mock_weapon_roll.assert_called_once()
            self.assertTrue(strike.is_critical_hit)
            self.assertFalse(strike.is_critical_miss)
            self.assertGreater(strike.damage, 0)
            self.assertTrue(strike.is_hit)
            self.assertFalse(strike.is_miss)
        
    def test_critical_hit_multiplier(self):
        weapon = weapons.Spear()
        self.assertEqual(weapon.critical_hit_multiplier, 2)

    def test_get_attack_type(self):
        self.assertEqual(weapons.Spear().get_attack_type(), 'spear')
        self.assertEqual(weapons.Dagger().get_attack_type(), 'dagger')
        self.assertEqual(weapons.LongSword().get_attack_type(), 'sword')
        self.assertEqual(weapons.ShortSword().get_attack_type(), 'sword')
        self.assertEqual(weapons.LongBow().get_attack_type(), 'arrow')
        self.assertEqual(weapons.ShortBow().get_attack_type(), 'arrow')
        self.assertEqual(weapons.Spear().get_attack_type(), 'spear')

    def test_is_critical_miss(self):
        weapon = weapons.Spear()
        self.assertTrue(weapon.is_critical_miss(1))
        self.assertFalse(weapon.is_critical_miss(2))

    def test_is_critical_strike(self):
        weapon = weapons.Spear()

        weapons.WeaponStats.get_critical_hit_range = Mock(return_value=range(19,21))
        self.assertTrue(weapon.is_critical_strike(20))
        self.assertTrue(weapon.is_critical_strike(19))
        self.assertFalse(weapon.is_critical_strike(18))
        self.assertFalse(weapon.is_critical_strike(21))

    def test_is_throwable(self):
        self.assertTrue(weapons.Spear().is_throwable)
        self.assertFalse(weapons.ShortSword().is_throwable)
        self.assertTrue(weapons.Dagger().is_throwable)
        self.assertFalse(weapons.LongBow().is_throwable)
        self.assertFalse(weapons.IronArrow().is_throwable)

    def test_max_damage(self):
        #1d8
        weapons.WeaponStats.get_damage_dice = Mock(return_value=[1,8])
        self.assertEqual(weapons.Spear().max_damage, 8)

        #2d10
        weapons.WeaponStats.get_damage_dice = Mock(return_value=[2,10])
        self.assertEqual(weapons.Spear().max_damage, 20)

    def test_min_damage(self):
        #1d8
        weapons.WeaponStats.get_damage_dice = Mock(return_value=[1,8])
        self.assertEqual(weapons.Spear().min_damage, 1)
        weapons.WeaponStats.get_damage_dice.assert_called_once()

        #2d10
        weapons.WeaponStats.get_damage_dice = Mock(return_value=[2,10])
        self.assertEqual(weapons.Spear().min_damage, 2)
        weapons.WeaponStats.get_damage_dice.assert_called_once()
