import unittest
from players import players, character_classes, skills
from game_items import armor, weapons
from common.rules import GameRules
from common import base_classes

class test_battle(unittest.TestCase):
    tried_sneak_attack = False

    def test_ranged_attack(self):
        player = players.Player(character_classes.Thief())
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
        player = players.Player(character_classes.Thief())
        player.equip_weapon(weapons.Dagger())
        player.equip_armor(armor.LightArmor())
        player.strength_base = 15
        player.dexterity_base = 10

        player.max_hit_points = 100

        goblin = players.Goblin()
        self.assertGreaterEqual(goblin.hit_points,2,"Hit points set")

        goblin.max_hit_points = 100

        player_def = player.get_armor_class()
        goblin_def = goblin.get_armor_class()
        print "Player Hit Points: {}".format(player.hit_points)
        print "Player def: {}".format(player_def)
        print "Player attack modifier: {}".format(player.attack_modifier())
        print "Player damage modifier: {}".format(player.damage_modifier())
        print "---"
        print "Goblin Hit Points: {}".format(goblin.hit_points)
        print "Goblin def: {}".format(goblin_def)
        print "Goblin attack modifier: {}".format(goblin.attack_modifier())
        print "Goblin damage modifier: {}".format(goblin.damage_modifier())
        print "---"
        dice_roll, modifer = GameRules.roll_initiative_check(goblin)
        gob_init_check = dice_roll + modifer
        dice_roll, modifer = GameRules.roll_initiative_check(player)
        player_init_check = dice_roll + modifer 
        print "Goblin Initiative: {} ({})".format(gob_init_check,goblin.initiative_modifier())
        print "Player Initiative: {} ({})".format(player_init_check,player.initiative_modifier())
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


