import boto3
from boto3.dynamodb.conditions import Attr, Key
import json
from questgame.common import test_constants, constants
import decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

class db(object):
    """Manages database connectivity"""

    def __init__(self, user):
        self.__user = user

    def _table(self): return self._connect().Table('GameData')

    def _connect(self):
        if test_constants.UNITTEST_DB_LOCAL:
            return boto3.resource('dynamodb',
                              aws_access_key_id="anything",
                              aws_secret_access_key="anything",
                              region_name="us-west-2",
                              endpoint_url="http://{}:{}".format(constants.DYNAMO_TEST_SERVER, constants.DYNAMO_TEST_PORT))
        else:

            return boto3.resource('dynamodb',
                              region_name="us-west-2")

    def does_user_exist(self):
        table = self._table()
        response = table.get_item(
            Key={
                'user': self.__user
            }
        )
        print(json.dumps(response, indent=4, cls=DecimalEncoder))
        return 'Item' in response.keys()

    def delete_user(self, name):
        table = self._table()
        response = table.delete_item(
            Key={
                'user': self.__user
            }
        )
        print(json.dumps(response, indent=4, cls=DecimalEncoder))

    def get_item(self, name=None):
        table = self._table()

        if name:
            response = table.query(
                KeyConditionExpression=Key('user').eq(self.__user),
                ProjectionExpression='content.{}'.format(name)
            )
        else:
            response = table.query(
                KeyConditionExpression=Key('user').eq(self.__user)
            )
        print(json.dumps(response, indent=4, cls=DecimalEncoder))
        items = response['Items']
        if len(items) == 0 or len(items[0]) == 0:
            return None
        result = items[0]['content']
        if name:
            keys = name.split('.')
            for k in keys:
                result = result[k]
        return result

    def delete_item(self, name):
        table = self._table()
        keys = name.split('.')
        parent_key = None
        for i in range(len(keys)-1):
            if parent_key is None: parent_key = ''
            if i != 0: parent_key+='.'
            parent_key += keys[i]
        data = self.get_item(parent_key)
        del data[keys[len(keys)-1]]
        self.put_item(parent_key, data)

    def put_item(self, name, value):
        table = self._table()
        value = value

        if name is None:
            response = table.put_item(
               Item={
                    'user': self.__user,
                    'content': value
                })
            print(json.dumps(response, indent=4, cls=DecimalEncoder))
            return

        try:
            response = table.update_item(
                Key={
                    'user': self.__user,
                },
                UpdateExpression='SET content.{} = :value'.format(name),
                ExpressionAttributeValues={
                    ':value': value
                }
            )
            #table.meta.client.get_waiter('table_not_exists').wait(TableName='GameData')
            print(json.dumps(response, indent=4, cls=DecimalEncoder))
        except Exception, e:
            if '.' in name: raise AttributeError()
            response = table.put_item(
               Item={
                    'user': self.__user,
                    'content': {name:value}
                })
            print(json.dumps(response, indent=4, cls=DecimalEncoder))

    def store_json(self, name, file):
        data = ''
        with open(file) as data_file:    
            data = json.load(data_file)
        self.put_item(name,data)
