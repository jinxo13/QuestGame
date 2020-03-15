import unittest

from questgame.interface.controller import GameManager
from questgame.players.players import Player, Rat
from questgame import rooms
from questgame.rooms.room import Actions
from questgame.interface.alexa.utils import ReplyHelpers
from alexa_test_helpers import AlexaRequest, AlexaResponse
from alexa_control import app, game_manager
from alexa_client import AlexaClient
from questgame.game_items import items, spells, potions, weapons, armor

class Test_rooms(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        app.config['ASK_VERIFY_REQUESTS'] = False
        app.config['TESTING'] = True
        self.alexa_client = AlexaClient()
        
    def test_throw_actions(self):
        gm = game_manager
        player = gm.create_player('thief')
        gm.start_new_game('fred', player)
        user = gm.get_user('fred','test')
        user.set_room(rooms.CellRoom(player))
        room = user.room

        dagger = weapons.Dagger()
        #Throw item you don't have
        reply = room.throw(dagger, None)
        self.assertTrue('not carrying' in reply)
        print reply

        #Throw at non-existent item
        player.pickup(dagger)
        reply = room.throw(dagger, 'chest')
        self.assertTrue(ReplyHelpers.render_action_template('no_such_target', item_text=dagger.description) in reply)
        print reply

        #Throw item at door
        reply = room.throw(dagger, 'door')
        self.assertTrue('door' in reply)
        print reply
        self.assertTrue('you throw' in reply.lower())

    def test_eat_actions(self):
        gm = game_manager
        player = gm.create_player('mage')
        gm.start_new_game('fred', player)
        user = gm.get_user('fred','test')
        user.set_room(rooms.CellRoom(player))
        room = user.room

        #Cast at room item
        player.pickup(items.StaleBread())
        reply = room.eat(items.StaleBread())
        print reply
        self.assertTrue('you eat the' in reply.lower())

        reply = room.eat(items.StaleBread())
        print reply
        self.assertTrue('not carrying' in reply)

        reply = room.eat(items.LockPick())
        print reply
        self.assertTrue("can't eat" in reply.lower())

    def test_cast_actions(self):
        gm = game_manager
        player = gm.create_player('mage')
        gm.start_new_game('fred', player)
        user = gm.get_user('fred','test')
        user.set_room(rooms.CellRoom(player))
        room = user.room

        #Cast at room item
        door = room.get_room_item_by_name('door')
        reply = room.cast('fireball', door)
        print reply
        self.assertTrue('you cast' in reply.lower())

        #Cast spell you don't have
        reply = room.cast('open', door)
        print reply
        self.assertTrue("you can't cast" in reply.lower())

        #Cast at monster
        reply = room.cast('fireball', Rat())
        print reply
        self.assertTrue('you cast' in reply.lower())

    def test_cast_drink(self):
        gm = game_manager
        player = gm.create_player('mage')
        gm.start_new_game('fred', player)
        user = gm.get_user('fred','test')
        user.set_room(rooms.CellRoom(player))
        room = user.room

        #Can't drink that
        reply = room.drink(weapons.Dagger())
        print reply
        self.assertTrue("you can't" in reply.lower())

        #Not carrying that
        reply = room.drink(items.Beer())
        print reply
        self.assertTrue("you're not carrying" in reply.lower())

        player.pickup(items.Beer())
        reply = room.drink(items.Beer())
        self.assertTrue("you drink the beer" in reply.lower())
        print reply

        player.pickup(potions.HealingPotion())
        reply = room.drink(potions.HealingPotion())
        self.assertTrue("you drink the healing potion" in reply.lower())
        print reply


    def test_describe(self):
        gm = game_manager
        player = gm.create_player('mage')
        gm.start_new_game('fred', player)
        user = gm.get_user('fred','test')
        user.set_room(rooms.CellRoom(player))
        room = user.room

        reply = room.describe(weapons.Dagger())
        print reply

    def test_store(self):
        gm = game_manager
        player = gm.create_player('mage')
        gm.start_new_game('fred', player)
        user = gm.get_user('fred','test')

        room = rooms.room.StoreRoom(player, [weapons.Weapon, armor.Armor])
        room.store_item(weapons.Dagger(), is_unlimited=True)
        room.store_item(weapons.WoodArrow(10))

        player.pickup(items.Gold())
        self.assertFalse(player.is_carrying(weapons.Dagger()))
        result = room.buy('dagger')
        self.assertTrue("you buy the dagger" in result.lower())
        print result
        self.assertTrue(player.is_carrying(weapons.Dagger()))
        self.assertTrue(player.money == 0.8)
        result = room.buy('dagger', 2)
        self.assertTrue("you buy the daggers" in result.lower())
        print result
        self.assertTrue(player.inventory.count_items(weapons.Dagger()) == 3)
        self.assertTrue(player.money == 0.4)

        result = room.buy('healing potion')
        self.assertTrue("you can't buy" in result.lower())
        print result

        result = room.buy('light armor')
        self.assertTrue("you can't buy" in result.lower())
        print result

        #Not enough money
        result = room.buy('daggers',3)
        self.assertTrue("you don't have enough" in result.lower())
        print result
        self.assertTrue(player.inventory.count_items(weapons.Dagger()) == 3)
        self.assertTrue(player.money == 0.4)

        result = room.sell('healing potion')
        self.assertTrue("you couldn't sell" in result.lower())
        print result

        player.pickup(armor.LightArmor())
        result = room.sell('light armor')
        self.assertTrue("you sell the light armor" in result.lower())
        print result

        result = room.sell('dagger')
        self.assertTrue("you sell the dagger" in result.lower())
        print result
        self.assertTrue(player.inventory.count_items(weapons.Dagger()) == 2)
        self.assertTrue(player.money == 5.6)
        result = room.buy('light armor')
        self.assertTrue(player.money == 0.6)

        result = room.whats_for_sale()
        self.assertTrue("10 wood arrows" in result.lower())
        print result

        #Sell too many
        result = room.sell('daggers', 3)
        self.assertTrue("you're not carrying enough" in result.lower())
        print result
        self.assertTrue(player.inventory.count_items(weapons.Dagger()) == 2)
        self.assertTrue(player.money == 0.6)

        #Buy all the arrows
        player.pickup(items.Gold(3))
        result = room.buy('wood arrows', 10)
        self.assertTrue("you buy the wood arrows" in result.lower())
        print result

        result = room.whats_for_sale()
        self.assertTrue("wood arrows" not in result.lower())
        print result

        result = room.buy('wood arrow')
        self.assertTrue("you can't buy" in result.lower())
        print result

    def test_CellRoom_Thief(self):
        gm = game_manager
        player = gm.create_player('thief')
        gm.start_new_game('fred', player)
        user = gm.get_user('fred','test')
        user.set_room(rooms.CellRoom(player))

        #What can I do
        request = AlexaRequest(self.app, user_id='fred', application_id='quest_game')
        request.set_intent('WhatCanIDoIntent')
        response = request.post()
        print response.get_output_text()
        self.assertTrue('you could search the room' in response.get_output_text().lower())
        player = user.room.player

        #Search room
        request = AlexaRequest(self.app, user_id='fred', application_id='quest_game')
        request.set_intent('SearchIntent')
        request.set_slots([request.create_slot('sitem','room')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('cellroom_search') in response.get_output_text())
        player = user.room.player

        #What can I do
        request = AlexaRequest(self.app, user_id='fred', application_id='quest_game')
        request.set_intent('WhatCanIDoIntent')
        response = request.post()
        print response.get_output_text()
        self.assertTrue('you could open the loose stone' in response.get_output_text().lower())

        #Search room
        request.set_intent('SearchIntent')
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('cellroom_search') in response.get_output_text())

        #What can I do
        request.set_intent('WhatCanIDoIntent')
        response = request.post()
        print response.get_output_text()

        #Pull loose stone
        request.set_intent('PullIntent')
        request.set_slots([request.create_slot('item','loose stone')])
        response = request.post()
        print response.get_output_text()
        lockpick = items.LockPick()
        self.assertTrue(ReplyHelpers.render_room_template('cellroom_pull_stone') in response.get_output_text())
        self.assertTrue(ReplyHelpers.render_room_template('cellroom_pull_stone_full',item_text=lockpick.description) in response.get_output_text())
        self.assertTrue(player.is_carrying(lockpick))

        #What can I do
        request = AlexaRequest(self.app, user_id='fred', application_id='quest_game')
        request.set_intent('WhatCanIDoIntent')
        response = request.post()
        print response.get_output_text()
        self.assertTrue('you could search the straw' in response.get_output_text().lower())

        #Pull loose stone again
        request.set_intent('OpenIntent')
        request.set_slots([request.create_slot('oitem','loose stone')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('cellroom_pull_stone') in response.get_output_text())
        self.assertTrue(ReplyHelpers.render_room_template('cellroom_pull_stone_empty') in response.get_output_text())

        #Pull door
        request.set_intent('PullIntent')
        request.set_slots([request.create_slot('item','door')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('locked',item='door') in response.get_output_text())

        #Open something
        request.set_intent('OpenIntent')
        request.set_slots([])
        response = request.post()
        print response.get_output_text()

        request.set_intent('SelectItemIntent')
        request.set_slots([request.create_slot('ditem','door')])
        response = request.post(request.session_id)
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('locked',item='door') in response.get_output_text())

        #Pull chest
        request.set_intent('PullIntent')
        request.set_slots([request.create_slot('item','chest')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('no_such_room_item',room='room',action='pull') in response.get_output_text())

        #Describe dagger
        request.set_intent('DescribeItemIntent')
        request.set_slots([request.create_slot('ditem','dagger')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('no_such_room_item',room='room', action='describe') in response.get_output_text())

        #Open door
        request.set_intent('OpenIntent')
        request.set_slots([request.create_slot('oitem','door')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('locked', item='door') in response.get_output_text())

        #Open window
        request.set_intent('OpenIntent')
        request.set_slots([request.create_slot('oitem','window')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('cellroom_barred_window_open_cannot') in response.get_output_text())

        #Pickup bread
        request.set_intent('PickupIntent')
        request.set_slots([request.create_slot('ditem','bread')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('pickup_item', item=items.StaleBread().description) in response.get_output_text())

        #Pickup bread
        request.set_intent('PickupIntent')
        request.set_slots([request.create_slot('ditem','bread')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('no_such_room_item',action='pickup',room='room') in response.get_output_text())

        #Drop bread
        request.set_intent('DropIntent')
        request.set_slots([request.create_slot('ditem','bread')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('drop_item', item=items.StaleBread().description) in response.get_output_text())

        #Pickup bread
        request.set_intent('PickupIntent')
        request.set_slots([request.create_slot('ditem','bread')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('pickup_item', item=items.StaleBread().description) in response.get_output_text())

        #Search floor
        request.set_intent('SearchIntent')
        request.set_slots([request.create_slot('sitem','floor')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('search_item',item='floor') in response.get_output_text())

        picked = False
        while not picked:
            #Picklock door
            request.set_intent('PickLockIntent')
            request.set_slots([request.create_slot('oitem','door')])
            response = request.post()
            picked = ReplyHelpers.render_room_template('picklock_success', item='door') in response.get_output_text()
            self.assertTrue(ReplyHelpers.render_room_template('picklock_success', item='door') in response.get_output_text() or
                            ReplyHelpers.render_room_template('picklock_fail', item='door') in response.get_output_text())
            
        player = user.player
        player.max_hit_points = 100
        player.strength_base = 15
        player.dexterity_base = 10

        #Search straw
        request.set_intent('SearchIntent')
        request.set_slots([request.create_slot('sitem','straw')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('search_item',item='straw') in response.get_output_text())

        #Rat has attacked
        #Describe rat
        monster = user.room.get_monsters()[0]
        monster.max_hit_points = 20
        request.set_intent('DescribeItemIntent')
        request.set_slots([request.create_slot('ditem','rat')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_descr_template('descr_rat',hit_points=monster.hit_points) in response.get_output_text())

        while len(user.room.get_alive_monsters())>0:
            if player.get_item(weapons.Dagger()).count == 4:
                request.set_intent('ThrowTargetIntent')
                request.set_slots([request.create_slot('target','rat'), request.create_slot('titem','dagger')])
            elif player.get_item(weapons.Dagger()).count == 3:
                request.set_intent('ThrowIntent')
                request.set_slots([request.create_slot('titem','dagger')])
            else:
                request.set_intent('StrikeIntent')
                request.set_slots([request.create_slot('target','rat')])
                if player.get_item(weapons.Dagger()).count == 1:
                    player.pickup(weapons.Dagger(3))

            response = request.post()
            print response.get_output_text()
        
        #search rat
        request.set_intent('SearchIntent')
        request.set_slots([request.create_slot('sitem','rat')])
        response = request.post()
        print response.get_output_text()
        #self.assertTrue(ReplyHelpers.render_room_template('search_item',item='rat') in response.get_output_text())

        request.set_intent('DescribeItemIntent')
        request.set_slots([request.create_slot('ditem','rat')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_descr_template('descr_rat',hit_points=monster.hit_points) in response.get_output_text())

        #Describe dagger
        request.set_intent('DescribeItemIntent')
        request.set_slots([request.create_slot('ditem','dagger')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_descr_template('descr_dagger') in response.get_output_text())

        #Open door
        request.set_intent('OpenIntent')
        request.set_slots([request.create_slot('oitem','door')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('door_open') in response.get_output_text())

        #Go back to cell
        request.set_intent('OpenIntent')
        request.set_slots([request.create_slot('oitem','door')])
        response = request.post()
        print response.get_output_text()

        #Open door again
        request.set_intent('OpenIntent')
        request.set_slots([request.create_slot('oitem','door')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('door_already_open') in response.get_output_text())

        #Unlock open door
        request.set_intent('UnlockIntent')
        request.set_slots([request.create_slot('oitem','door')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('not_locked',item='door') in response.get_output_text())

        #Close an open door
        request.set_intent('CloseIntent')
        request.set_slots([request.create_slot('oitem','door')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('close', item='door') in response.get_output_text())

        #Describe dagger
        request.set_intent('DescribeItemIntent')
        request.set_slots([request.create_slot('ditem','dagger')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_descr_template('descr_dagger') in response.get_output_text())

    def test_CellRoom_Mage(self):
        gm = game_manager
        player = gm.create_player('mage')
        gm.start_new_game('fred', player)
        user = gm.get_user('fred','test')
        user.set_room(rooms.CellRoom(player))
        user.save_game()

        user.load_game()

        #Search room
        request = AlexaRequest(self.app, user_id='fred', application_id='quest_game')
        request.set_intent('SearchIntent')
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('cellroom_search') in response.get_output_text())
        player = user.room.player

        #Pull loose stone
        request.set_intent('PullIntent')
        request.set_slots([request.create_slot('item','loose stone')])
        response = request.post()
        print response.get_output_text()
        scroll = items.Scroll(spells.UnlockSpell())
        self.assertTrue(ReplyHelpers.render_room_template('cellroom_pull_stone') in response.get_output_text())
        self.assertTrue(ReplyHelpers.render_room_template('cellroom_pull_stone_full',item_text=scroll.description) in response.get_output_text())
        self.assertTrue(player.is_carrying(scroll))


        unlocked = False
        while not unlocked:
            #Cast open at door
            if user.player.mana_points < 1:
                user.player.pickup(potions.ManaPotion())
                user.player.drink_potion(potions.ManaPotion())
            request.set_intent('CastTargetIntent')
            request.set_slots([request.create_slot('target','door'), request.create_slot('spell','unlock')])
            response = request.post()
            print response.get_output_text()
            unlocked = not user.room.get_room_item_by_name('door').is_locked
            
        player = user.player
        player.max_hit_points = 100
        player.strength_base = 15
        player.dexterity_base = 10

        #Search straw
        request.set_intent('SearchIntent')
        request.set_slots([request.create_slot('sitem','straw')])
        response = request.post()
        print response.get_output_text()
        self.assertTrue(ReplyHelpers.render_room_template('search_item',item='straw') in response.get_output_text())

        #Rat has attacked
        rat = user.room.get_monsters()[0]
        rat.max_hit_points = 20
        while len(user.room.get_alive_monsters())>0:
            if user.player.mana_points < 1:
                user.player.pickup(potions.ManaPotion())
                user.player.drink(potions.ManaPotion())
            request.set_intent('CastIntent')
            request.set_slots([request.create_slot('spell','fireball')])
            response = request.post()
            print response.get_output_text()
        
        #search rat
        request.set_intent('SearchIntent')
        request.set_slots([request.create_slot('sitem','rat')])
        response = request.post()
        print response.get_output_text()
        #self.assertTrue(ReplyHelpers.render_room_template('search_item',item='rat') in response.get_output_text())


if __name__ == '__main__':
    unittest.main()
