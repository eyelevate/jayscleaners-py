from unittest import TestCase

from classes.mainScreen import MainScreen

class MainScreen_TestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls._mainScreen = MainScreen
        print('open class')

    @classmethod
    def tearDownClass(cls):
        del cls._mainScreen
        print('close class')

    def setUp(self):
        self.username = 'onedough83'
        pass

    def tearDown(self):
        self.username = None
        print('setup close')
    #unit tests
    def test_update_info_returnString(self):
        message = self._mainScreen.update_info(self)
        self.assertEqual(message, 'Last updated today')

    def test_check_username_returnUsername(self):
        check_username = self._mainScreen.check_username(self, value= self.username)
        self.assertEqual(check_username, self.username)