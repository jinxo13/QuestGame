import unittest
from questgame.common import test_constants

class Test_test1(unittest.TestCase):
    def test__DEPLOY_OK(self):
        self.assertFalse(test_constants.ASK_RUN_WITH_DEBUG_ON)
        self.assertFalse(test_constants.UNITTEST_DB_LOCAL)
        self.assertFalse(test_constants.UNITTEST_TEST_INTENTS)

if __name__ == '__main__':
    unittest.main()
