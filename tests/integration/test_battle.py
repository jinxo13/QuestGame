import unittest
from questgame.players import players, character_classes, skills
from questgame.game_items import armor, weapons
from questgame.common.rules import GameRules
from questgame.common import base_classes

class test_battle(unittest.TestCase):
    tried_sneak_attack = False

    def test_ranged_attack(self):
        player = players.Thief()
        player.equip_weapon(weapons.ShortBow())
        player.equip_armor(armor.LightArmor())
        player.strength_base = 15
        player.dexterity_base = 10
        player.max_hit_points = 100

        player.pickup(weapons.SteelArrow())
        player.pickup(weapons.SteelArrow())

        goblin = players.Goblin()
        
        base_classes.Observer(goblin)
        base_classes.Observer(player)

        self.assertEqual(player.inventory.count, 2)
        player.strike(goblin)
        self.assertEqual(player.inventory.count, 1)
        w = player.get_equipped_weapon()
        self.assertEqual(w.ammo_count(player), 1)

    def test_goblin(self):
        player = players.Thief()
        player.equip_weapon(weapons.Dagger())
        player.equip_armor(armor.LightArmor())
        player.strength_base = 15
        player.dexterity_base = 10

        player.max_hit_points = 100

        goblin = players.Goblin()
        goblin.affect(player, players.Effects.Heal, 0)
        self.assertGreaterEqual(goblin.hit_points,2,"Hit points set")

        goblin.max_hit_points = 100

        player_def = player.get_defense()
        goblin_def = goblin.get_defense()
        print "Player Hit Points: {}".format(player.hit_points)
        print "Player def: {}".format(player_def)
        print "Player ability modifier: {}".format(player.determine_ability_modifier())
        print "Player proficiency modifier: {}".format(player.determine_proficiency_bonus())
        print "---"
        print "Goblin Hit Points: {}".format(goblin.hit_points)
        print "Goblin def: {}".format(goblin_def)
        print "Goblin ability modifier: {}".format(goblin.determine_ability_modifier())
        print "Goblin proficiency modifier: {}".format(goblin.determine_proficiency_bonus())
        print "---"
        dice_roll = GameRules.roll_initiative_check(goblin)
        gob_init_check = dice_roll.total
        dice_roll = GameRules.roll_initiative_check(player)
        player_init_check = dice_roll.total
        print "Goblin Initiative: {} ({})".format(gob_init_check,goblin.initiative_modifier)
        print "Player Initiative: {} ({})".format(player_init_check,player.initiative_modifier)
        if gob_init_check > player_init_check:
            print "Goblin was quicker to react, and starts first"
        else:
            print "Player was quicker to react, and starts first"
        print "---"

        #Attacks
        a = base_classes.Observer(goblin)
        b = base_classes.Observer(player)

        done_sneak_attack = False

        while not goblin.is_dead and not player.is_dead:
            if gob_init_check < player_init_check:
                player.strike(goblin)
                if not done_sneak_attack:
                    player.skill_attack(skills.SneakAttack(), goblin)
                    done_sneak_attack = True
                goblin.strike(player)
            else:
                goblin.strike(player)
                player.strike(goblin)
                if not done_sneak_attack:
                    player.skill_attack(skills.SneakAttack(), goblin)
                    done_sneak_attack = True


