import unittest
import questgame.game_items.spells as spells
from questgame.common.rules import Effects

class mockPlayerClass:
    def __init__(self):
        self.spell_attack_attribute = spells.ATTRIBUTES.WISDOM
    def get_spell_save_will(self):
        return 3
        
class mockPlayer:
    def __init__(self, name):
        self.health = 100
        self.name = name
        self.is_undead = False
        self.character_class = mockPlayerClass()
        self.is_monster = False
        self.level = 3
        self.hit_points = 20
        self.mana_points = 5
        self.wisdom_modifier = 2
    def notify_observers_log(self, msg):
        pass
    def notify_observers_reply(self, msg):
        pass
    @property
    def is_dead(self):
        return self.health <= 0
    def get_reply_key(self, key):
        return self.name+'_'+key
    def affect(self, source, effect, params):
        if effect == Effects.Damage: self.wound(params)
        elif effect == Effects.Heal: self.heal(params)
    def heal(self, amount):
        self.health = min(100, self.health + amount)
    def wound(self, amount):
        self.health = max(0, self.health - amount)
    def class_name(self):
        return self.__class__.__name__
    def get_attribute_modifier(self, attr):
        return 1
    def can_cast_spell(self, spell):
        return self.mana_points >= spell.level
    def add_mana(self, val):
        self.mana_points = min(max(0, self.mana_points + val),40)
    def get_spell_proficiency(self, spell):
        return True

class mockItem:
    def __init__(self, name):
        self.name = name
        self.spell_resistance = 0
        self.open = False
        self.locked = False
        self.hit_points = 10
    def class_name(self):
        return self.__class__.__name__
    def affect(self, source, effect, params):
        pass
    def open_with_spell(self, spell, caster):
        self.open = True
    def close_with_spell(self, spell, caster):
        self.open = False
    def lock_with_spell(self, spell, caster):
        self.locked = True
    def unlock_with_spell(self, spell, caster):
        self.locked = False

class TestSpells(unittest.TestCase):

#Test casting harmful spell - FireballSpell
#Test casting effect spell - OpenSpell, CloseSpell, UnlockSpell, LockSpell, HarmSpell, HealSpeal

    def test_fireball_spell(self):
        #Fireball spell does damage to target
        player = mockPlayer('player')
        player.level = 10
        monster = mockPlayer('monster')
        monster.is_monster = True
        monster.level = 1
        monster.wisdom_modifier = -4

        spell = spells.FireballSpell()
        monster.health = 100
        player.mana_points = 10
        for _i in range(10):
            spell.cast(player, monster)
            if monster.health < 100: break
        self.assertLess(monster.health, 100, 'monster hurt by fireball')
        self.assertLess(player.mana_points, 10, 'player used mana casting spell')

    def test_fireball_spell_item(self):
        #Fireball spell does damage to target
        player = mockPlayer('player')
        chest = mockItem('chest')
        spell = spells.FireballSpell()
        spell.cast(player, chest)

    def test_open_spell(self):
        #open spell opens openable objects
        player = mockPlayer('player')
        chest = mockItem('chest')
        spell = spells.OpenSpell()
        self.assertFalse(chest.open)
        self.assertTrue(spell.cast(player, chest))
        self.assertTrue(chest.open)

    def test_close_spell(self):
        #open spell closes openable objects
        player = mockPlayer('player')
        chest = mockItem('chest')
        chest.open = True
        spell = spells.CloseSpell()
        self.assertTrue(chest.open)
        self.assertTrue(spell.cast(player, chest))
        self.assertFalse(chest.open)

    def test_unlock_spell(self):
        #Unlock spell unlocks openable objects
        #If already unlocked it's 100% effective....
        player = mockPlayer('player')
        chest = mockItem('chest')
        chest.locked = True
        spell = spells.UnlockSpell()
        self.assertTrue(chest.locked)
        self.assertTrue(spell.cast(player, chest))
        self.assertFalse(chest.locked)

    def test_lock_spell(self):
        #Lock spell locks openable objects
        #If already locked it's 100% effective....
        player = mockPlayer('player')
        chest = mockItem('chest')
        chest.locked = False
        spell = spells.LockSpell()
        self.assertFalse(chest.locked)
        self.assertTrue(spell.cast(player, chest))
        self.assertTrue(chest.locked)

    def test_harm_spell(self):
        #Harm spell harms target (or heals undead)
        player = mockPlayer('player')
        spell = spells.HarmSpell()
        self.assertEqual(player.health, 100)
        self.assertTrue(spell.cast(player, player))
        self.assertLess(player.health, 100)

        #Try undead
        player.is_undead = True
        self.assertTrue(spell.cast(player, player))
        self.assertEqual(player.health, 100)

    def test_heal_spell(self):
        #Heal spell heals target (or harms undead)
        player = mockPlayer('player')
        spell = spells.HealSpell()
        player.health = 90
        self.assertEqual(player.health, 90)
        self.assertTrue(spell.cast(player, player))
        self.assertGreater(player.health, 90)

        #Try undead
        player.is_undead = True
        self.assertTrue(spell.cast(player, player))
        self.assertLess(player.health, 90)
