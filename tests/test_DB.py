import unittest
import boto3
import os
from db import database
from db.save_load_game import GameManager

class Test_dynamodb(unittest.TestCase):
    
    def test__DB_game_state(self):
        user = 'test_user'
        db = database.db(user)
        game_state = {}
        game_state[GameManager.STATE_ROOM] = {'x':1}
        game_state[GameManager.STATE_DOOR] = {'x':2}
        game_state[GameManager.STATE_PLAYER] = {'x':3}

        gm = GameManager(user)
        save_name = 'game1'
        gm.save_game(save_name, game_state)
        result = gm.load_game(save_name)
        self.assertEqual(result[GameManager.STATE_ROOM],{'x':1})
        self.assertEqual(result[GameManager.STATE_DOOR],{'x':2})
        self.assertEqual(result[GameManager.STATE_PLAYER],{'x':3})

        gm.save_state(save_name, GameManager.STATE_DOOR, {'y':1})
        result = gm.load_state(save_name, GameManager.STATE_DOOR)
        self.assertEqual(result,{'y':1})

        gm.delete_game(save_name)
        result = gm.load_game(save_name)
        self.assertIsNone(result[GameManager.STATE_ROOM])

        db.delete_user(user)

    def test__DB_item(self):
        db = database.db('test_user')
        item = db.get_item('zzz')
        self.assertIsNone(item)

        db.put_item('xxx', 'fred')
        item = db.get_item('xxx')
        self.assertEqual(item, 'fred')

        db.put_item('xxx', 'bob')
        item = db.get_item('xxx')
        self.assertEqual(item, 'bob')

        db.put_item('xxx', {'x':1})
        item = db.get_item('xxx')
        self.assertEqual(item, {'x':1})

        db.delete_item('xxx')
        item = db.get_item('xxx')
        self.assertIsNone(item)
    
        #Test setting/getting child attributes
        db.put_item('xxx', {'x': {'y':2}})
        item = db.get_item('xxx.x')
        self.assertEqual(item, {'y':2})

        db.put_item('xxx.x', {'y':3})
        item = db.get_item('xxx')
        self.assertEqual(item, {'x': {'y':3}})

        db.delete_item('xxx.x.y')
        item = db.get_item('xxx')
        self.assertEqual(item, {'x': {}})

        self.assertTrue(db.does_user_exist())
        db.delete_user('test_user')
        self.assertFalse(db.does_user_exist())

    def test__DB_SETUP(self):
        # Get the service resource.
        db = database.db('test_user')
        dynamodb = db._connect()

        try:
            table = dynamodb.Table('GameData')
            table.delete()
            table.meta.client.get_waiter('table_not_exists').wait(TableName='GameData')
        except:
            pass

        # Create the DynamoDB table.
        table = dynamodb.create_table(
            TableName='GameData',
            KeySchema=[
                {
                    'AttributeName': 'user',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'user',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        # Wait until the table exists.
        table.meta.client.get_waiter('table_exists').wait(TableName='GameData')

        # Print out some data about the table.
        self.assertEqual(table.item_count,0)

        #Test user existence
        db = database.db('test_user')
        self.assertFalse(db.does_user_exist())

        #Load some data
        db.store_json('test','./config/rooms.json')

        self.assertTrue(db.does_user_exist())

if __name__ == '__main__':
    unittest.main()
