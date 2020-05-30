import unittest
from questgame.game_items import spells, items, armor, weapons
from questgame.players import players
from questgame.rooms import CellRoom

class Test_save_create_state(unittest.TestCase):
    
    def test_spell_state(self):
        spell = spells.FireballSpell()
        state = spell.get_state()
        spell2 = spells.Spell.create_from_state(state)
        self.assertTrue(spell.__class__ == spell2.__class__)

    def test_scroll_state(self):
        spell = spells.FireballSpell()
        scroll = items.Scroll(spell)
        state = scroll.get_state()
        scroll2 = items.Item.create_from_state(state)
        self.assertTrue(scroll.__class__ == scroll2.__class__)

    def test_item_state(self):
        dagger = weapons.Dagger(3)
        state = dagger.get_state()
        dagger2 = items.Item.create_from_state(state)
        self.assertEqual(dagger.__class__, dagger2.__class__)
        self.assertEqual(dagger.count, 3)
        self.assertEqual(dagger.count, dagger2.count)

    def test_player_state(self):
        spell = spells.FireballSpell()
        player = players.Mage()
        player.learn_spell(spell)
        state = player.get_state()

        axe = weapons.Axe()
        player.pickup(axe)
        player.equip_weapon(axe)
        lightArmor = armor.LightArmor()
        player.pickup(lightArmor)
        player.equip_armor(lightArmor)

        player.add_experience(300)
        self.assertEqual(player.level, 2)
        player.pickup(items.LockPick())

        player2 = players.Player.create_from_state(state)
        self.assertTrue(player.__class__ == player2.__class__)
        self.assertTrue(player.get_equipped_weapon().__class__ == weapons.Axe)
        self.assertTrue(player.get_equipped_armor().__class__ == armor.LightArmor)
        self.assertTrue(player.is_carrying(items.LockPick()))

    def test_room_state(self):
        player = players.Mage()
        room = CellRoom(player)
        state = room.get_state()
        room_copy = room.create_from_state(state)

        self.assertEqual(room.__class__, room_copy.__class__)

if __name__ == '__main__':
    unittest.main()
