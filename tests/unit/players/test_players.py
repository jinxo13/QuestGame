import unittest
import math
import json
import mock
from mock import Mock, PropertyMock
import questgame.players.players as players
from tests.helpers.mock_helpers import MockHelper

class TestPlayer(unittest.TestCase):

    def test_add_experience(self):
        player = players.Thief()

       # Level - [Experience, Proficiency]
       # 1: [300,2],
       # 2: [900,2],
       # 3: [2700,2],

        #Test adding experience and moving levels
        self.assertEqual(player.level, 1)
        player.add_experience(299)
        self.assertEqual(player.level, 1)
        player.add_experience(1)
        self.assertEqual(player.level, 2)

    def test_add_mana(self):
        #Test adding mana
        player = players.Thief()
        player.max_mana_points = 20
        self.assertEqual(player.mana_points, 0, 'no mana')
        player.add_mana(20)
        self.assertEqual(player.mana_points, 20, 'full mana')
        player.add_mana(-10)
        self.assertEqual(player.mana_points, 10, 'some mana')
        try:
            player.mana_points = 1
            self.assertTrue(False, "can't set mana")
        except:
            self.assertTrue(True, "can't set mana")

        #Test limits, mana can't be < 0, or > max mana
        self.assertEqual(player.mana_points, 10, 'still some mana')
        player.add_mana(30)
        self.assertEqual(player.mana_points, 20, 'max mana')
        player.add_mana(-50)
        self.assertEqual(player.mana_points, 0, 'min mana')

    def test_proficiency_bonus(self):
        #Attack bonus increases by level
        player = players.Thief()
        bonus = {
            1: [0, 2],
            2: [300, 2],
            3: [900, 2],
            4: [2700, 2],
            5: [6500, 3],
            6: [14000, 3],
            7: [23000, 3],
            8: [34000, 3],
            9: [48000, 4],
            10: [64000, 4],
            11: [85000, 4],
            12: [100000, 4],
            13: [120000, 5],
            14: [140000, 5],
            15: [165000, 5],
            16: [195000, 5],
            17: [225000, 6],
            18: [265000, 6],
            19: [305000, 6],
            20: [355000, 6]
        }

        last_exp = 0
        for level in bonus.keys():
            player.add_experience(bonus[level][0] - last_exp)
            last_exp = bonus[level][0]
            self.assertEqual(player.level, level)
            self.assertEqual(player.proficiency_bonus, bonus[level][1])
    
    def test_other_attack_bonus(self):
        #Add an attack modifier
        player = players.Thief()
        self.assertEqual(player.level, 1)
        self.assertEqual(player.other_attack_bonus, 0)
        player.add_modifier('BECAUSE',players.ATTRIBUTES.ATTACK, 3)
        self.assertEqual(player.other_attack_bonus, 3)
        player.remove_modifier('BECAUSE')
        self.assertEqual(player.other_attack_bonus, 0)

    def test_determine_ability_modifier(self):
        #Attack modifier is based on the weapons modifier attribute
        player = players.Thief()
        import questgame.game_items.weapons as weapons
        
        butter_knife = Mock(spec=weapons.Weapon)
        player.is_carrying = Mock(return_value=True)
        self.assertTrue(player.equip_weapon(butter_knife))
        butter_knife_modifier = PropertyMock(return_value=[players.ATTRIBUTES.DEXTERITY])
        type(butter_knife).modifier_attributes = butter_knife_modifier
        butter_knife.get_modifier_value = Mock(return_value=0)
        
        self.assertEqual(player.dexterity, 11)
        butter_knife.get_modifier_value.assert_called_once
        butter_knife_modifier.assert_called_once

        #Should be round down of (x - 10)/2
        attack = player.determine_ability_modifier()
        self.assertEqual(attack, math.floor((11 - 10)/2))

        type(butter_knife).modifier_attributes = PropertyMock(return_value=[players.ATTRIBUTES.INTELLIGENCE])
        self.assertEqual(player.intelligence, 8)
        attack = player.determine_ability_modifier()
        self.assertEqual(attack, math.floor((8 - 10)/2))

    def test_can_act(self):
        #Player can act as long as not stunned, unconscious or dead
        #Use mage as mocks impact other tests
        player = players.Thief()
        self.assertTrue(player.can_act)

        with MockHelper.Property(player, 'is_dead', return_value=False) as is_dead_mock, \
            MockHelper.Property(player, 'is_unconscious', return_value=False) as is_unconscious_mock, \
            MockHelper.Property(player, 'is_stunned', return_value=False) as is_stunned_mock:

            self.assertTrue(player.can_act)
            #Check each one was called
            is_dead_mock.assert_called_once()
            is_stunned_mock.assert_called_once()
            is_unconscious_mock.assert_called_once()

            #Stunned
            is_stunned_mock.return_value=True
            self.assertFalse(player.can_act)
            is_stunned_mock.return_value=False

            #Unconscious
            is_unconscious_mock.return_value=True
            self.assertFalse(player.can_act)
            is_unconscious_mock.return_value=False

            #Dead
            is_dead_mock.return_value=True
            self.assertFalse(player.can_act)
            is_dead_mock.return_value=False
            self.assertTrue(player.can_act)

    def test_can_cast_spell(self):
        #Knows spell
        #Has a sufficient level
        #Has enough mana
        #Can act
        smiteSpell = Mock()
        smiteSpell.level = 1

        player = players.Thief()
        player.max_mana_points = 4
        player.add_mana(4)

        with MockHelper.Property(player, 'can_act', return_value=True) as can_act_mock:
        
            player.knows_spell = Mock(return_value=True)
            self.assertTrue(player.can_cast_spell(smiteSpell))
        
            #Ensure methods called as expected
            can_act_mock.assert_called_once()
            player.knows_spell.assert_called_once()

            #Not enough mana
            player.add_mana(-4)
            self.assertFalse(player.can_cast_spell(smiteSpell))
            player.add_mana(4)
            self.assertTrue(player.can_cast_spell(smiteSpell))

            #Not a high enough level
            smiteSpell.level = 2
            self.assertFalse(player.can_cast_spell(smiteSpell))
            smiteSpell.level = 1
            self.assertTrue(player.can_cast_spell(smiteSpell))
            
            #Can't act
            can_act_mock.return_value=False
            self.assertFalse(player.can_act)
            self.assertFalse(player.can_cast_spell(smiteSpell))

            #Doesn't know spell
            player.knows_spell = Mock(return_value=False)
            self.assertFalse(player.knows_spell(smiteSpell))
            self.assertFalse(player.can_cast_spell(smiteSpell))

    def test_has_skill(self):
        player = players.Thief()
        skill = Mock()
        player.character_class.is_skill_proficient = Mock(return_value=True)
        self.assertTrue(player.has_skill(skill))
        player.character_class.is_skill_proficient.assert_called_once()

        player.character_class.is_skill_proficient = Mock(return_value=False)
        self.assertFalse(player.has_skill(skill))

    def test_can_picklock(self):
        #Can act, has a lock pick and the lock picking skill
        player = players.Thief()
        player.is_carrying = Mock(return_value=True)
        player.has_skill = Mock(return_value=True)
        
        #Stash can_act
        with MockHelper.Property(player, 'can_act', return_value=True) as mock_can_act:
            self.assertTrue(player.can_picklock())

            #No lockpick
            mock_is_carrying = Mock(return_value=False)
            player.is_carrying = mock_is_carrying
            self.assertFalse(player.can_picklock())

            #Can't act
            mock_is_carrying.return_value=True
            self.assertTrue(player.can_picklock())
            mock_can_act.return_value=False
            self.assertFalse(player.can_picklock())
            
            #No skill
            mock_can_act.return_value=True
            self.assertTrue(player.can_picklock())
            player.has_skill = Mock(return_value=False)
            self.assertFalse(player.can_picklock())

    def test_carry_capacity(self):
        #Rule = current strength * 15
        player = players.Thief()
        start_strength = player.strength
        self.assertEqual(player.carry_capacity, player.strength * 15)
        player.add_modifier('BONUS', players.ATTRIBUTES.STRENGTH, 2)
        self.assertEqual(player.carry_capacity, (start_strength + 2) * 15)

    def test_carry_weight(self):
        #Nothing to test
        player = players.Thief()
        self.assertEqual(player.carry_weight, 0, 'Start with nothing')

    def test_cast(self):
        #Cast a spell
        player = players.Thief()
        rat = players.Rat()
        
        spell = Mock()
        spell.cast = Mock(return_value=True)
        #Calls spell.cast which returns true or false which is passed through
        self.assertTrue(player.cast(spell, rat))
        spell.cast = Mock(return_value=False)
        self.assertFalse(player.cast(spell, rat))

    def test_character_class(self):
        player = players.Thief()
        self.assertTrue(player.character_class, players.character_classes.Thief)

        player = players.Goblin
        self.assertTrue(player.character_class, players.character_classes.Goblin)

    def test_charisma(self):
        player = players.Thief()
        self.assertEqual(player.charisma, player.get_attribute_current(players.ATTRIBUTES.CHARISMA))

    def test_is_weapon_equipped(self):
        player = players.Thief()
        fists = Mock()
        player.get_equipped_weapon = Mock(return_value=fists)
        self.assertTrue(player.is_weapon_equipped(fists))

        mace=Mock()
        self.assertFalse(player.is_weapon_equipped(mace))

    def test_is_armor_equipped(self):
        player = players.Thief()
        fur_armor = Mock()
        player.get_equipped_armor = Mock(return_value=fur_armor)
        self.assertTrue(player.is_armor_equipped(fur_armor))

        leather_armor=Mock()
        self.assertFalse(player.is_weapon_equipped(leather_armor))

    def test_class_name(self):
        player = players.Thief()
        self.assertEqual(players.Thief.__name__, player.class_name)

    def test_constitution(self):
        player = players.Thief()
        self.assertEqual(player.constitution, player.get_attribute_current(players.ATTRIBUTES.CONSITUTION))

    def test_constitution_modifier(self):
        player = players.Thief()
        self.assertEqual(player.constitution_modifier, player.get_modifier_value(players.ATTRIBUTES.CONSITUTION))
        
    def test_create_from_state(self):
        attributes = {
            str(players.ATTRIBUTES.STRENGTH): 9,
            str(players.ATTRIBUTES.WISDOM): 4
        }
        state = {
            'class': 'Thief',
            'module': 'questgame.players.players',
            'max_hit_points': 10,
            'hit_points': 9,
            'max_mana_points': 15,
            'mana_points': 11,
            'is_dead': False,
            'items': [],
            'learned_spells': [],
            'attributes': json.dumps(attributes)
        }
        #state = players.Thief().get_state()
        thief = players.Thief()
        thief = players.Player.create_from_state(state)
        self.assertEqual(thief.__class__.__name__, 'Thief')
        self.assertEqual(thief.max_hit_points, 10)
        self.assertEqual(thief.hit_points, 9)
        self.assertEqual(thief.max_mana_points, 15)
        self.assertEqual(thief.mana_points, 11)
        self.assertFalse(thief.is_unconscious)
        self.assertFalse(thief.is_dead)
        self.assertEqual(thief.strength, 9)
        self.assertEqual(thief.wisdom, 4)
        self.assertEqual(thief.dexterity, 0)

    def test_default_armor(self):
        import questgame.game_items.armor as armor
        player = players.Thief()
        self.assertTrue(isinstance(player.default_armor, armor.BodyArmor))

        player = players.Rat()
        self.assertTrue(isinstance(player.default_armor, armor.FurArmor))

    def test_default_weapon(self):
        import questgame.game_items.weapons as weapons
        player = players.Thief()
        self.assertTrue(isinstance(player.default_weapon, weapons.Fists))

        player = players.Rat()
        self.assertTrue(isinstance(player.default_weapon, weapons.Claws))

    def test_defense_bonus(self):
        player = players.Thief()
        self.assertEqual(player.defense_bonus, 0)

    def test_description(self):
        player = players.Thief()
        self.assertIsNotNone(player.description)

    def test_dexterity(self):
        player = players.Thief()
        self.assertEqual(player.dexterity, player.get_attribute_current(players.ATTRIBUTES.DEXTERITY))

    def test_dexterity_modifier(self):
        player = players.Thief()
        self.assertEqual(player.dexterity_modifier, player.get_modifier_value(players.ATTRIBUTES.DEXTERITY))

    def test_drink(self):
        player = players.Thief()
        #Potion or Drink and carrying it
        
        #Drink
        import questgame.game_items.items as items
        import questgame.game_items.potions as potions
        beer = Mock(spec=items.Drink)
        player.is_carrying = Mock(return_value=True)
        player.get_rid_of_one = Mock()
        self.assertTrue(player.drink(beer))

        #Potion
        beer = Mock(spec=potions.Potion)
        self.assertTrue(player.drink(beer))

        #Other
        beer = Mock()
        self.assertFalse(player.drink(beer))

        #Not carrying
        beer = Mock(spec=potions.Potion)
        player.is_carrying = Mock(return_value=False)
        self.assertFalse(player.drink(beer))

    def test_drop(self):
        player = players.Thief()
        penny  = self.get_mock_item()

        #Must be carrying item, then calls remove - which returns the item
        player.is_carrying = Mock(return_value=True)
        player.remove_item = Mock(return_value=penny)
        self.assertEqual(player.drop(penny), penny)

        #not carrying
        player.is_carrying = Mock(return_value=False)
        self.assertFalse(player.drop(penny))

    def test_eat(self):
        player = players.Thief()
        #Food and carrying it
        
        #Food
        import questgame.game_items.items as items
        bagel = Mock(spec=items.Food)
        player.is_carrying = Mock(return_value=True)
        player.get_rid_of_one = Mock()
        self.assertTrue(player.eat(bagel))

        #Other
        bagel = Mock()
        self.assertFalse(player.eat(bagel))

        #Not carrying
        bagel = Mock(spec=items.Food)
        player.is_carrying = Mock(return_value=False)
        self.assertFalse(player.eat(bagel))

    def test_equip_armor(self):
        #Check default armor
        player = players.Thief()
        self.assertEqual(player.get_equipped_armor(), player.default_armor)

        #Equip something that isn't armor
        fake_armor = Mock()
        self.assertFalse(player.equip_armor(fake_armor))

        #Not carrying
        good_armor = self.get_mock_armor()
        player.is_carrying = Mock(return_value=False)
        self.assertFalse(player.equip_armor(good_armor))
        player.is_carrying.assert_called_once()

        #Equip Armor
        player.is_carrying = Mock(return_value=True)
        self.assertTrue(player.equip_armor(good_armor))

        #Equip None, should be default
        try:
            player.equip_armor(None)
        except AttributeError:
            self.assertTrue(True, 'None is not valid')
        self.assertEqual(player.get_equipped_armor(), good_armor)

    def test_equip_weapon(self):
        #Check default armor
        player = players.Thief()
        self.assertEqual(player.get_equipped_weapon(), player.default_weapon)

        #Equip something that isn't armor
        fake_weapon = Mock()
        self.assertFalse(player.equip_weapon(fake_weapon))

        #Not carrying
        good_weapon = self.get_mock_weapon()
        player.is_carrying = Mock(return_value=False)
        self.assertFalse(player.equip_weapon(good_weapon))
        player.is_carrying.assert_called_once()

        #Equip Weapon
        player.is_carrying = Mock(return_value=True)
        self.assertTrue(player.equip_weapon(good_weapon))

        #Equip None, should be default
        try:
            player.equip_weapon(None)
        except AttributeError:
            self.assertTrue(True, 'None is not valid')
        self.assertEqual(player.get_equipped_weapon(), good_weapon)

    def test_get_attribute_base(self):
        player = players.Thief()
        self.assertEqual(player.get_attribute_base(players.ATTRIBUTES.STRENGTH),10)

    def test_get_attribute_current(self):
        player = players.Thief()
        self.assertEqual(player.get_attribute_current(players.ATTRIBUTES.STRENGTH),10)

    def test_get_attribute_modifier(self):
        player = players.Thief()
        
        #Confirm attribute values
        self.assertEqual(player.dexterity_base, 11)
        self.assertEqual(player.strength_base, 10)
        attr_val = player.get_attribute_modifier(players.ATTRIBUTES.STRENGTH)
        #Should be round down of (x - 10)/2
        self.assertEqual(attr_val, math.floor((10 - 10)/2))
        attr_val = player.get_attribute_modifier(players.ATTRIBUTES.DEXTERITY)
        self.assertEqual(attr_val, math.floor((11 - 10)/2))

        #Try a couple of attributes, should select the highest
        attr_val = player.get_attribute_modifier([players.ATTRIBUTES.STRENGTH, players.ATTRIBUTES.DEXTERITY])
        self.assertEqual(attr_val, math.floor((11 - 10)/2))


    def test_get_defense(self):
        player = players.Thief()
        self.assertEqual(player.get_defense(), 10)

    def test_get_equipped_armor(self):
        player = players.Thief()
        rat = players.Rat()
        #Just returns currently assigned armor
        self.assertEqual(player.get_equipped_armor(), player.default_armor)
        #TODO: Probably shouldn't allow this....
        player.is_carrying = Mock(return_value=True)
        self.assertTrue(player.equip_armor(rat.default_armor))
        self.assertEqual(player.get_equipped_armor(), rat.default_armor)

    def test_get_equipped_weapon(self):
        player = players.Thief()
        rat = players.Rat()
        #Just returns currently assigned armor
        self.assertEqual(player.get_equipped_weapon(), player.default_weapon)
        #TODO: Probably shouldn't allow this....
        player.is_carrying = Mock(return_value=True)
        self.assertTrue(player.equip_weapon(rat.default_weapon))
        self.assertEqual(player.get_equipped_weapon(), rat.default_weapon)

    def get_mock_item(self, spec=None):
        item = Mock()
        if spec != None:
            item = Mock(spec=spec)
        item.weight = 1
        item.count = 1
        item.single_weight = 1
        item.create_from_state = Mock(return_value=item)
        return item

    def get_mock_armor(self):
        import questgame.game_items.armor as armor
        return self.get_mock_item(spec=armor.Armor)

    def get_mock_weapon(self):
        import questgame.game_items.weapons as weapons
        return self.get_mock_item(spec=weapons.Weapon)

    def get_mock_scroll(self):
        import questgame.game_items.items as items
        return self.get_mock_item(items.Scroll)

    def get_mock_beer(self):
        import questgame.game_items.items as items
        return self.get_mock_item(items.Beer)

    def test_get_item(self):
        player = players.Thief()
        penny = self.get_mock_item()

        #Get an item from inventory
        #Returns False if no such item
        self.assertFalse(player.get_item(penny))

        self.assertTrue(player.pickup(penny))
        self.assertEqual(player.get_item(penny), penny)

    def test_get_item_by_name(self):
        player = players.Thief()
        penny = self.get_mock_item()

        #Get an item from inventory
        #Returns False if no such item
        self.assertFalse(player.get_item_by_name('penny'))

        self.assertTrue(player.pickup(penny))
        penny.is_match = Mock(return_value=False)
        self.assertFalse(player.get_item_by_name('penny'))
        penny.is_match.assert_called_once()

        penny.is_match = Mock(return_value=True)
        self.assertEqual(player.get_item_by_name('penny'), penny)

    def test_get_reply_key(self):
        player = players.Thief()
        rat = players.Rat()
        self.assertEqual(player.get_reply_key('key'), 'player_key')
        self.assertEqual(rat.get_reply_key('key'), 'monster_key')

    def test_get_rid_of_one(self):
        player = players.Thief()
        beer = self.get_mock_beer()

        #Not carrying a penny
        #Carrying 2 then 1 should be left
        #Carrying 1 then none should be left
        
        #Not carrying
        self.assertFalse(player.get_rid_of_one(beer))
        
        #Carrying 2
        beer.count = 2
        self.assertTrue(player.pickup(beer))
        self.assertTrue(player.get_rid_of_one(beer))
        self.assertTrue(player.is_carrying(beer))

        #Drop second one
        self.assertTrue(player.get_rid_of_one(beer))
        self.assertFalse(player.is_carrying(beer))
        self.assertFalse(player.get_rid_of_one(beer))

    def test_get_state(self):
        player = players.Thief()
        state = player.get_state()
        self.assertIsInstance(state, dict)

    def test_give(self):
        player = players.Thief()
        rat = players.Rat()

        penny = self.get_mock_item()

        #Can give
        player.is_carrying = Mock(return_value=True)
        player.remove_item = Mock(return_value=True)
        self.assertTrue(player.give(penny, rat))

        #Not carrying
        player.is_carrying = Mock(return_value=False)
        self.assertFalse(player.give(penny, rat))

        #Can't remove
        player.is_carrying = Mock(return_value=True)
        player.remove_item = Mock(return_value=False)
        self.assertFalse(player.give(penny, rat))

    def test_has_armor_equipped(self):
        player = players.Thief()
        self.assertFalse(player.has_weapon_equipped())

        dagger = self.get_mock_weapon()
        player.is_carrying = Mock(return_value=True)
        self.assertTrue(player.equip_weapon(dagger))
        self.assertTrue(player.has_weapon_equipped())

    def test_has_weapon_equipped(self):
        player = players.Thief()
        self.assertFalse(player.has_armor_equipped())

        armor = self.get_mock_armor()
        player.is_carrying = Mock(return_value=True)
        self.assertTrue(player.equip_armor(armor))
        self.assertTrue(player.has_armor_equipped())

    def test_heal(self):
        player = players.Thief()

        #Returns ture if any healing occurred
        #Hit points can exceed max_hit_points
        #Heal amount can't be <= 0

        #No healing
        self.assertFalse(player.heal(-1))
        self.assertFalse(player.heal(0))
        
        #<0
        self.assertGreater(player.max_hit_points, 0)
        self.assertEqual(player.hit_points, player.max_hit_points)
        #Ok full health
        self.assertFalse(player.heal(1))
        self.assertEqual(player.hit_points, player.max_hit_points)

        #Wound
        self.assertTrue(player.wound(1))
        self.assertLess(player.hit_points, player.max_hit_points)
        self.assertTrue(player.heal(20))
        self.assertEqual(player.hit_points, player.max_hit_points)

        #Can't heal if dead
        self.assertTrue(player.wound(1))

        #Mock class method
        with MockHelper.Property(player, 'is_dead', return_value=True) as mock_is_dead:
            self.assertFalse(player.heal(1))
            mock_is_dead.assert_called_once()

            mock_is_dead.return_value=False
            self.assertTrue(player.heal(1))

    def test_hit_points(self):
        player = players.Thief()
        self.assertEqual(player.hit_points, player.max_hit_points)
         
    def test_initiative_modifier(self):
        player = players.Thief()
        self.assertEqual(player.initiative_modifier, player.get_modifier_value(players.ATTRIBUTES.INITIATIVE))

    def test_intelligence(self):
        player = players.Thief()
        self.assertEqual(player.intelligence, player.get_attribute_current(players.ATTRIBUTES.INTELLIGENCE))

    def test_intelligence_modifier(self):
        player = players.Thief()
        self.assertEqual(player.intelligence_modifier, player.get_modifier_value(players.ATTRIBUTES.INTELLIGENCE))

    def test_inventory(self):
        player = players.Thief()
        #Inventory exists
        self.assertEqual(player.inventory.weight, 0)
        
    def test_is_carrying(self):
        #nothing to test, relies on inventory
        player = players.Thief()
        self.assertFalse(player.is_carrying(Mock()))

    def test_is_dead(self):
        player = players.Thief()
        self.assertFalse(player.is_dead)

        #Ensure save on death
        with MockHelper.Method(players.GameRules, 'roll_death_save', return_value=20) as mock_death_save:
            self.assertTrue(player.wound(player.max_hit_points))
            self.assertEqual(player.hit_points, 0)
            self.assertFalse(player.is_dead)
            mock_death_save.assert_called()

        #Massive damage - save has no effect
        with MockHelper.Method(players.GameRules, 'roll_death_save', return_value=20) as mock_death_save:
            self.assertTrue(player.wound(player.max_hit_points))
            self.assertEqual(player.hit_points, 0)
            self.assertTrue(player.is_dead)
            mock_death_save.assert_not_called()

        #Massive damage - save has no effect
        with MockHelper.Method(players.GameRules, 'roll_death_save', return_value=20) as mock_death_save:
            player = players.Thief()
            self.assertTrue(player.wound(player.max_hit_points*2))
            self.assertTrue(player.is_dead)
            mock_death_save.assert_not_called()

        #Large damage - save has an effect
        with MockHelper.Method(players.GameRules, 'roll_death_save', return_value=20) as mock_death_save:
            player = players.Thief()
            self.assertTrue(player.wound(player.max_hit_points*2-1))
            self.assertFalse(player.is_dead)
            mock_death_save.assert_called_once()

    def test_is_encumbered(self):
        player = players.Thief()

        #Stash class methods
        with MockHelper.Property(player, 'carry_weight', return_value=0) as mock_carry_weight, \
            MockHelper.Property(player, 'carry_capacity', return_value=10) as mock_carry_capacity:

            #weight < capacity
            self.assertFalse(player.is_encumbered)
            mock_carry_weight.assert_called_once()
            mock_carry_capacity.assert_called_once()

            #weight = capacity
            mock_carry_weight.return_value=10
            self.assertFalse(player.is_encumbered)

            #weight > capacity
            mock_carry_weight.return_value=11
            self.assertTrue(player.is_encumbered)


    def test_is_fighter(self):
        player = players.Fighter()
        self.assertTrue(player.is_fighter)
        self.assertFalse(player.is_mage)
        self.assertFalse(player.is_thief)
        self.assertFalse(player.is_ranger)

    def test_is_in_battle(self):
        player = players.Fighter()
        self.assertFalse(player.is_in_battle)
        
    def test_is_looted(self):
        player = players.Fighter()
        self.assertFalse(player.is_looted)

    def test_is_mage(self):
        player = players.Mage()
        self.assertTrue(player.is_mage)
        self.assertFalse(player.is_thief)
        self.assertFalse(player.is_fighter)
        self.assertFalse(player.is_ranger)

    def test_is_match(self):
        player = players.Thief()
        self.assertTrue(player.is_match('Thief'))
        self.assertTrue(player.is_match('thief'))
        self.assertTrue(player.is_match('THIEF'))

    def test_is_monster(self):
        player = players.Thief()
        monster = players.Rat()
        self.assertTrue(monster.is_monster)
        self.assertFalse(player.is_monster)

    def test_is_ranger(self):
        player = players.Ranger()
        self.assertTrue(player.is_ranger)
        self.assertFalse(player.is_thief)
        self.assertFalse(player.is_fighter)
        self.assertFalse(player.is_mage)

    def test_is_stunned(self):
        player = players.Ranger()
        self.assertFalse(player.is_stunned)

    def test_is_thief(self):
        player = players.Thief()
        self.assertTrue(player.is_thief)
        self.assertFalse(player.is_mage)
        self.assertFalse(player.is_fighter)
        self.assertFalse(player.is_ranger)
    def test_is_unconscious(self):
        player = players.Thief()
        self.assertFalse(player.is_dead)
        self.assertFalse(player.is_unconscious)

        #Ensure Save from death, but not max save
        with MockHelper.Method(players.GameRules, 'roll_death_save', return_value=19) as mock_death_save:
            self.assertTrue(player.wound(player.max_hit_points))
            self.assertEqual(player.hit_points, 0)
            self.assertFalse(player.is_dead)
            self.assertTrue(player.is_unconscious)
            #Can't wound if no points
            self.assertFalse(player.wound(0))
            mock_death_save.assert_called_once()

        #Massive damage, no save
        with MockHelper.Method(players.GameRules, 'roll_death_save', return_value=20) as mock_death_save:
            self.assertTrue(player.wound(player.max_hit_points))
            self.assertEqual(player.hit_points, 0)
            self.assertTrue(player.is_dead)
            self.assertFalse(player.is_unconscious)
            #Dead can't wound anymore
            self.assertFalse(player.wound(player.max_hit_points))
            mock_death_save.assert_not_called()

        #Massive damage, no save
        with MockHelper.Method(players.GameRules, 'roll_death_save', return_value=20) as mock_death_save:
            player = players.Thief()
            self.assertTrue(player.wound(player.max_hit_points*2))
            self.assertTrue(player.is_dead)
            self.assertFalse(player.is_unconscious)
            mock_death_save.assert_not_called()

        #Large damage, save matters
        with MockHelper.Method(players.GameRules, 'roll_death_save', return_value=20) as mock_death_save:
            player = players.Thief()
            self.assertTrue(player.wound(player.max_hit_points*2-1))
            self.assertFalse(player.is_dead)
            self.assertEqual(player.hit_points, 0)
            self.assertTrue(player.is_unconscious)
            mock_death_save.assert_called_once()

    def test_is_undead(self):
        player = players.Thief()
        self.assertFalse(player.is_undead)

        player = players.ZombieRat()
        self.assertTrue(player.is_undead)

    def test_learn_spell(self):
        player = players.Thief()
        import questgame.game_items.spells as spells
        shrink = Mock(spec=spells.Spell)
        shrink.level = 1
        self.assertFalse(player.knows_spell(shrink))

        #Learn a spell
        self.assertEqual(player.level, shrink.level)
        self.assertTrue(player.learn_spell(shrink))
        self.assertTrue(player.knows_spell(shrink))
        #Learn again
        self.assertFalse(player.learn_spell(shrink))

        #Not a spell
        fake_spell = Mock()
        fake_spell.level = 1
        self.assertFalse(player.learn_spell(shrink))

        #Too advanced
        grow = Mock(spec=spells.Spell)
        grow.level = 2
        self.assertFalse(player.learn_spell(grow))

    def test_level(self):
        player = players.Thief()
        self.assertEqual(player.level, 1)

        player.add_experience(9999999)
        self.assertEqual(player.level, 20)

    def test_loot_body(self):
        player = players.Thief()
        rat = players.Rat()
        zombie_rat = players.ZombieRat()
        another_rat = players.Rat()

        #Inventory is empty
        #Is looted
        #Inventory has 1 item
        #Inventory has 2 items

        #Empty
        self.assertEqual(player.loot_body(rat), [])

        #Already looted
        self.assertFalse(player.loot_body(rat))

        penny = self.get_mock_item()
        quarter = self.get_mock_item()

        #1 item
        self.assertTrue(zombie_rat.pickup(penny))
        self.assertEqual(player.loot_body(zombie_rat), [penny])
        self.assertTrue(player.is_carrying(penny))
        self.assertFalse(zombie_rat.is_carrying(penny))

        #2 items
        self.assertTrue(another_rat.pickup(penny))
        self.assertTrue(another_rat.pickup(quarter))
        self.assertEqual(player.loot_body(another_rat), [penny, quarter])

        self.assertTrue(player.is_carrying(penny))
        self.assertTrue(player.is_carrying(quarter))
        self.assertFalse(another_rat.is_carrying(penny))
        self.assertFalse(another_rat.is_carrying(quarter))

    def test_mana_points(self):
        player = players.Thief()
        self.assertEqual(player.mana_points, 0)

        player = players.Mage()
         #TODO fix? intitial mana = 0?

        #Can't directly change
        try:
            player.mana_points = 10
            self.assertTrue(False)
        except AttributeError:
            self.assertTrue(True)

        #Can't be negative
        self.assertGreater(player.max_mana_points, 0)
        player.add_mana(-10)
        self.assertEqual(player.mana_points, 0)
        
        #Can't exceed max mana points
        self.assertGreater(player.max_mana_points, 0)
        player.add_mana(player.max_mana_points + 10)
        self.assertEqual(player.mana_points, player.max_mana_points)

        #Just right
        player.add_mana(-player.max_mana_points + 2)
        self.assertEqual(player.mana_points, 2)

    def test_money(self):
        #Return money in inventory
        player = players.Thief()
        self.assertEqual(player.money, 0)

        #Other testing covered in Inventory

    def test_pickup(self):
        player = players.Thief()

        #If scroll learn it
        #If weapon equip it - if no weapon equipped and proficient
        #If armor equip it - if no armor equipped and proficient

        #Scroll
        scroll = self.get_mock_scroll()
        player.learn_spell = Mock(return_value=True)
        self.assertTrue(player.pickup(scroll))
        player.learn_spell.assert_called_once()

        #Weapon
        weapon = self.get_mock_weapon()
        weapon.get_modifier_value = Mock(return_value=0)

        #Not proficient
        player.character_class.is_weapon_proficient = Mock(return_value=False)
        self.assertFalse(player.has_weapon_equipped())
        self.assertTrue(player.pickup(weapon))
        self.assertFalse(player.has_weapon_equipped())
        self.assertNotEqual(player.get_equipped_weapon(), weapon)

        #Proficient
        player.character_class.is_weapon_proficient = Mock(return_value=True)
        self.assertFalse(player.has_weapon_equipped())
        self.assertTrue(player.pickup(weapon))
        self.assertTrue(player.has_weapon_equipped())
        self.assertEqual(player.get_equipped_weapon(), weapon)

        #Already equipped
        another_weapon = self.get_mock_weapon()
        self.assertTrue(player.pickup(another_weapon))
        self.assertTrue(player.has_weapon_equipped())
        self.assertEqual(player.get_equipped_weapon(), weapon)

        #Armor
        myarmor = self.get_mock_armor()
        myarmor.get_modifier_value = Mock(return_value=0)

        #Not proficient
        player.character_class.is_armor_proficient = Mock(return_value=False)
        self.assertFalse(player.has_armor_equipped())
        self.assertTrue(player.pickup(myarmor))
        self.assertFalse(player.has_armor_equipped())
        self.assertNotEqual(player.get_equipped_armor(), myarmor)

        #Proficient
        player.character_class.is_armor_proficient = Mock(return_value=True)
        self.assertFalse(player.has_armor_equipped())
        self.assertTrue(player.pickup(myarmor))
        self.assertTrue(player.has_armor_equipped())
        self.assertEqual(player.get_equipped_armor(), myarmor)

        #Already equipped
        another_armor = self.get_mock_armor()
        self.assertTrue(player.pickup(another_armor))
        self.assertTrue(player.has_armor_equipped())
        self.assertEqual(player.get_equipped_armor(), myarmor)

    def test_remove_item(self):
        player = players.Thief()

        #Not carrying item does nothing
        #Removing equipped armor resets to default
        #Removing equipped weapon resets to default

        #Armor
        myarmor = self.get_mock_armor()
        myarmor.get_modifier_value = Mock(return_value=0)

        #Nothing to remove
        self.assertFalse(player.remove_item(myarmor))

        #Remove equipped armor
        player.character_class.is_armor_proficient = Mock(return_value=True)
        self.assertTrue(player.pickup(myarmor))
        self.assertEqual(player.get_equipped_armor(), myarmor)
        self.assertTrue(player.has_armor_equipped())
        self.assertTrue(player.remove_item(myarmor))
        self.assertNotEqual(player.get_equipped_armor(), myarmor)
        self.assertFalse(player.has_armor_equipped())

        #Remove equipped weapon
        weapon = self.get_mock_weapon()
        weapon.get_modifier_value = Mock(return_value=0)
        player.character_class.is_weapon_proficient = Mock(return_value=True)
        self.assertTrue(player.pickup(weapon))
        self.assertTrue(player.has_weapon_equipped())
        self.assertEqual(player.get_equipped_weapon(), weapon)
        self.assertTrue(player.remove_item(weapon))
        self.assertNotEqual(player.get_equipped_weapon(), weapon)
        self.assertFalse(player.has_weapon_equipped())

    def test_skill_attack(self):
        player = players.Thief()
        backstab = Mock()
        rat = players.Rat()

        backstab.damage = Mock(return_value=2)

        #Doesn't have skill
        player.has_skill = Mock(return_value=False)
        self.assertFalse(player.skill_attack(backstab, rat))
        player.has_skill.assert_called_once()
         
        #Doesn't have skill
        player.has_skill = Mock(return_value=True)
        self.assertTrue(player.skill_attack(backstab, rat))

    def test_strength(self):
        player = players.Thief()
        self.assertEqual(player.strength, player.get_attribute_current(players.ATTRIBUTES.STRENGTH))

    def test_strength_modifier(self):
        player = players.Thief()
        self.assertEqual(player.strength_modifier, player.get_modifier_value(players.ATTRIBUTES.STRENGTH))

    def test_strike(self):
        player = players.Thief()
        rat = players.Rat()
        
        #Can't act
        with MockHelper.Property(player, 'can_act', return_value=False) as mock_can_act:
            self.assertFalse(player.strike(rat))
            mock_can_act.assert_called_once()

            mock_can_act.return_value=True
            strike = player.strike(rat)
            self.assertIsNotNone(strike.damage)

    def test_throw(self):
        player = players.Thief()
        rat = players.Rat()
        dagger = self.get_mock_weapon()
        not_a_dagger = self.get_mock_item()
        
        #Must be carrying item
        #Item must be a throwable weapon
        #Should decrease number of items when thrown
        #If none left then no longer carrying

        #Not carrying
        player.is_carrying = Mock(return_value=False)
        self.assertFalse(player.throw(dagger, rat))
        player.is_carrying.assert_called_once()

        #Not a weapon
        #TODO: Allow food to be thrown?
        player.is_carrying = Mock(return_value=True)
        self.assertFalse(player.throw(not_a_dagger, rat))

        #Not throwable
        #Mock class methods
        mock_is_throwable = PropertyMock(return_value=True)
        type(dagger).is_throwable = mock_is_throwable

        self.assertTrue(player.throw(dagger, rat))
        mock_is_throwable.assert_called_once()

    def test_determine_throw_bonus(self):
        player = players.Thief()
        self.assertEqual(player.determine_throw_bonus(), player.get_attribute_current(players.ATTRIBUTES.THROW))

    def test_wisdom(self):
        player = players.Thief()
        self.assertEqual(player.wisdom, player.get_attribute_current(players.ATTRIBUTES.WISDOM))
    def test_wisdom_modifier(self):
        player = players.Thief()
        self.assertEqual(player.wisdom_modifier, player.get_modifier_value(players.ATTRIBUTES.WISDOM))

    def test_wound(self):
        player = players.Thief()

        #Returns true if any wound occurred
        #Hit points can be < 0
        #Wound amount can't be <= 0

        #No healing
        self.assertFalse(player.wound(-1))
        self.assertFalse(player.wound(0))
        
        #<0
        self.assertGreater(player.max_hit_points, 0)
        self.assertEqual(player.hit_points, player.max_hit_points)
        
        #Ok full health
        self.assertTrue(player.wound(1))
        self.assertEqual(player.hit_points, player.max_hit_points-1)

        #Wound
        self.assertTrue(player.wound(player.max_hit_points-2))
        self.assertEqual(player.hit_points, 1)

        #Death
        self.assertTrue(player.wound(player.max_hit_points+1))
        self.assertEqual(player.hit_points, 0)
        self.assertTrue(player.is_dead)

        #Possible death
        death_count = 0
        for _i in range(100):
            player = players.Thief()
            self.assertEqual(player.hit_points, player.max_hit_points)
            self.assertTrue(player.wound(player.max_hit_points))
            if player.is_dead:
                death_count += 1
        self.assertGreater(death_count, 0)
        self.assertLess(death_count, 100)

    def test_deregister_observer(self): pass #Observable
    def test_notify_observers_log(self): pass #Observable
    def test_notify_observers_reply(self): pass #Observable
    def test_register_observer(self): pass #Observable

    def test_add_modifier(self): pass
    def test_get_modifier_value(self): pass
    def test_get_modifiers(self): pass
    def test_remove_modifier(self): pass
