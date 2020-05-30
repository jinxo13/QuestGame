from mock import PropertyMock, Mock
from enum import Enum
import inspect

class BaseMock:
    def __init__(self, ref, method_name, method):
        self.__stash = {'ref': ref, 'method_name': method_name, 'method': method}
        setattr(ref, method_name, self)

    def __enter__(self):
        return self

    def __exit__(self ,type, value, traceback):
        setattr(self.__stash['ref'], self.__stash['method_name'], self.__stash['method'])

    def revert(self):
        self.__exit__(None, None, None)


class PropMock(PropertyMock, BaseMock):
    def __init__(self, ref, method_name, return_value=False):
        PropertyMock.__init__(self, return_value=return_value)
        if inspect.isclass(ref):
            cls = ref
        else:
            cls = type(ref)
        mthd = None
        if method_name in cls.__dict__.keys():
            mthd = cls.__dict__[method_name]
        else:
            mthd = getattr(cls, method_name)
        if not isinstance(mthd, property):
            raise AttributeError('Passed method is not a property')
        BaseMock.__init__(self, cls, method_name, mthd)

class MethodMock(BaseMock, Mock):
    def __init__(self, ref, method_name, return_value=False):
        Mock.__init__(self, return_value=return_value)
        cls = ref
        method = None
        if not inspect.isclass(ref):
            #Object
            cls = type(ref)
            #method = getattr(ref, method_name)
            method = cls.__dict__[method_name]
            if not isinstance(method, staticmethod) and not isinstance(method, classmethod):
                method = getattr(ref, method_name)
        else:
            #Class
            method = cls.__dict__[method_name]
        if isinstance(method, staticmethod) or isinstance(method, classmethod):
            BaseMock.__init__(self, cls, method_name, method)
        else:
            BaseMock.__init__(self, ref, method_name, method)

class MockHelper:

    @staticmethod
    def Property(ref, method_name, return_value=False):
        return PropMock(ref, method_name, return_value)

    @staticmethod
    def Method(ref, method_name, return_value=False):
        return MethodMock(ref, method_name, return_value)

    @staticmethod
    def get_mock_item(spec=None):
        import questgame.game_items.items as items
        if spec == None: spec = items.Item
        item = Mock(spec=spec)
        item.weight = 1
        item.count = 1
        item.single_weight = 1
        item.create_from_state = Mock(return_value=item)
        item.get_bonus_value = Mock(return_value=0)
        return item

    @staticmethod
    def get_mock_armor():
        import questgame.game_items.armor as armor
        return MockHelper.get_mock_item(spec=armor.Armor)

    @staticmethod
    def get_mock_lock_spell():
        import questgame.game_items.spells as spells
        return MockHelper.get_mock_item(spec=spells.LockSpell)

    @staticmethod
    def get_mock_weapon():
        import questgame.game_items.weapons as weapons
        return MockHelper.get_mock_item(spec=weapons.Weapon)

    @staticmethod
    def get_mock_scroll():
        import questgame.game_items.items as items
        return MockHelper.get_mock_item(items.Scroll)

    @staticmethod
    def get_mock_beer():
        import questgame.game_items.items as items
        return MockHelper.get_mock_item(items.Beer)

    @staticmethod
    def get_mock_money():
        import questgame.game_items.items as items
        return MockHelper.get_mock_item(items.Money)
