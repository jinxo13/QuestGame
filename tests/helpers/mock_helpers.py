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
