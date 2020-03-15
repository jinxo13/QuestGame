import unittest
from mock_helpers import MockHelper

class MockMe(object):

    @staticmethod
    def static_method(): return True

    @classmethod
    def class_method(cls): return True

    @property
    def property_method(self): return True

    def method(self): return True

class TestMockHelper(unittest.TestCase):
    
    def test_property_mock(self):
        mockme = MockMe()
        
        stash = type(mockme).property_method
        self.assertEqual(stash, type(mockme).property_method)
        prop = MockHelper.Property(mockme, 'property_method')
        self.assertNotEqual(stash, type(mockme).property_method)

        prop.revert()
        self.assertEqual(stash, type(mockme).property_method)

    def test_property_mock_with(self):
        stash = MockMe.property_method
        with MockHelper.Property(MockMe, 'property_method'):
            self.assertNotEqual(stash, MockMe.property_method)
        self.assertEqual(stash, MockMe.property_method)

    def test_mock_static_method(self):
        stash = MockMe.static_method
        self.assertEqual(stash, MockMe.static_method)
        with MockHelper.Method(MockMe, 'static_method'):
            self.assertNotEqual(stash, MockMe.static_method)
        self.assertEqual(stash, MockMe.static_method)

    def test_mock_class_method(self):
        stash = MockMe.class_method
        self.assertEqual(stash, MockMe.class_method)
        with MockHelper.Method(MockMe, 'class_method'):
            self.assertNotEqual(stash, MockMe.class_method)
        self.assertEqual(stash, MockMe.class_method)

    def test_mock_method(self):
        mockme = MockMe()
        stash = mockme.method
        self.assertEqual(stash, mockme.method)
        with MockHelper.Method(mockme, 'method'):
            self.assertNotEqual(stash, mockme.method)
        self.assertEqual(stash, mockme.method)
