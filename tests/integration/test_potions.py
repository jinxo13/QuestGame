import unittest
import questgame.game_items.potions as potions
import questgame.players.players as players

class TestPotions(unittest.TestCase):

    def test_strength_potion(self):
        #Increases players strength
        player = players.Thief()
        index = potions.PlayerAttributes.STRENGTH
        player.add_bonus('ATTR_BONUS', index, 0)
        self.assertEqual(player.get_bonuses()['ATTR_BONUS'][index], 0, 'No strength bonus')
        strength_potion = potions.StrengthPotion()
        strength_potion.drink(player)
        self.assertEqual(player.get_bonuses()['ATTR_BONUS'][index], 2, 'Strength bonus')

    def test_healing_potion(self):
        #Increases players health
        player = players.Thief()
        potion = potions.HealingPotion()
        self.assertEqual(player.hit_points, 100, 'Healthy')
        potion.drink(player)
        self.assertGreater(player.hit_points, 100, 'Health increased')

    def test_healing_potion_undead(self):
        #Decreases undead health
        player = players.Thief()
        player.is_undead = True
        potion = potions.HealingPotion()
        self.assertEqual(player.hit_points, 100, 'Healthy')
        potion.drink(player)
        self.assertLess(player.hit_points, 100, 'Health decreased')

    def test_harm_potion(self):
        #Decreases player health
        player = players.Thief()
        potion = potions.HarmPotion()
        self.assertEqual(player.hit_points, 100, 'Healthy')
        potion.drink(player)
        self.assertLess(player.hit_points, 100, 'Health decreased')

    def test_harm_potion_undead(self):
        #Increases undead health
        player = players.ZombieRat()
        potion = potions.HarmPotion()
        self.assertEqual(player.hit_points, 100, 'Healthy')
        potion.drink(player)
        self.assertGreater(player.hit_points, 100, 'Health increased')

    def test_mana_potion(self):
        #Increases players mana
        player = players.Thief()

        potion = potions.ManaPotion()
        self.assertEqual(player.mana_points, 0, 'No mana')
        potion.drink(player)
        self.assertGreater(player.mana_points, 0, 'Mana increased')