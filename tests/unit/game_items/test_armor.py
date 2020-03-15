import unittest
import questgame.game_items.armor as armor

class mockPlayer:
    def __init__(self):
        self.armor = False
        self.dexterity_mod = 5

    def get_attribute_modifier(self, attr):
        return self.dexterity_mod

class TestArmor(unittest.TestCase):
    
    def test_light_armor(self):
        player = mockPlayer()
        lightArmor = armor.LightArmor()
        #AC Class + Modifier
        #11 + 5
        self.assertEqual(lightArmor.armor_total(player), 16, 'Armor AC - positive mod')

        player.dexterity_mod = -2
        self.assertEqual(lightArmor.armor_total(player), 9, 'Armor AC - negative mod')

    def test_heavey_armor(self):
        player = mockPlayer()
        heavyArmor = armor.HeavyArmor()
        #AC Class + Modifier (max 2)
        #13 + 2
        self.assertEqual(heavyArmor.armor_total(player), 15, 'Armor AC - positive mod')

        player.dexterity_mod = -2
        self.assertEqual(heavyArmor.armor_total(player), 11, 'Armor AC - negative mod')
        
