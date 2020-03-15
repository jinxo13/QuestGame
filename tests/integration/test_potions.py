import unittest

class TestPotions(unittest.TestCase):

    def test_strength_potion(self):
        #Increases players strength
        player = mock.Mock()
        index = potions.ATTRIBUTES.STRENGTH
        player.add_modifier('ATTR_BONUS', index, 0)
        self.assertEqual(player.attr['ATTR_BONUS'][index], 0, 'No strength bonus')
        strength_potion = potions.StrengthPotion()
        strength_potion.drink(player)
        self.assertEqual(player.attr['ATTR_BONUS'][index], 2, 'Strength bonus')

    def test_healing_potion(self):
        #Increases players health
        player = mock.Mock()
        potion = potions.HealingPotion()
        self.assertEqual(player.health, 100, 'Healthy')
        potion.drink(player)
        self.assertGreater(player.health, 100, 'Health increased')

    def test_healing_potion_undead(self):
        #Decreases undead health
        player = mock.Mock()
        player.is_undead = True
        potion = potions.HealingPotion()
        self.assertEqual(player.health, 100, 'Healthy')
        potion.drink(player)
        self.assertLess(player.health, 100, 'Health decreased')

    def test_harm_potion(self):
        #Decreases player health
        player = mockPlayer()
        potion = potions.HarmPotion()
        self.assertEqual(player.health, 100, 'Healthy')
        potion.drink(player)
        self.assertLess(player.health, 100, 'Health decreased')

    def test_harm_potion_undead(self):
        #Increases undead health
        player = mockPlayer()
        player.is_undead = True
        potion = potions.HarmPotion()
        self.assertEqual(player.health, 100, 'Healthy')
        potion.drink(player)
        self.assertGreater(player.health, 100, 'Health increased')

    def test_mana_potion(self):
        #Increases players mana
        player = mockPlayer()
        potion = potions.ManaPotion()
        self.assertEqual(player.mana, 0, 'No mana')
        potion.drink(player)
        self.assertGreater(player.mana, 0, 'Mana increased')