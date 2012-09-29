# Python standard library imports:
import unittest

# Our imports:
from ..utils import snake_to_mixed


class BaseTestCase(unittest.TestCase):
    """

    Extend this with your test cases to get some sweet shit!

    - Notes:
        - Never override the mixed case setup/teardown methods!  Those are how
         

    - Provides:

        - Instance methods:

            - `self.set_up()`: subclasses should use this for their
              test-by-test set up

            - `self.tear_down()`: subclasses should use this for their
              test-by-test tear down

        - Classmethods:

            - `cls.set_up_class():`:  subclasses should use this for their
              class-level set up

            - `cls.tear_down_class()`: subclasses should use this for their
              class-level tear down

        - Method aliases:

            - If you call any snake_case method call (instance method or
              classmethod) and that method does not exist, BaseTestCase will 
              attempt to call the mixedCase version, e.g.:
                - `self.assert_equal()`:  aliases self.assertEqual
                - `self.assert_true()`:  aliases self.assertTrue
    """

    # --------------------
    # Magic for snake_case
    # --------------------
    class __metaclass__(type):
        def __getattr__(cls, name):
            """
            
            This provides snake_case aliases for mixedCase classmethods.

            For instance, if you were to ask for `cls.tear_down_class`, and it
            didn't exist, you would transparently get a reference to
            `cls.tearDownClass` instead.

            """

            name = snake_to_mixed(name)
            return type.__getattribute__(cls, name)
        
    def __getattr__(self, name):
        """
        
        This provides snake_case aliases for mixedCase instance methods.

        For instance, if you were to ask for `self.assert_equal`, and it
        didn't exist, you would transparently get a reference to
        `self.assertEqual` instead.

        """

        mixed_name = snake_to_mixed(name)
        mixed_attr = None

        try:
            mixed_attr = object.__getattribute__(self, mixed_name)
        except:
            pass

        if mixed_attr:
            return mixed_attr

        return self.__getattribute__(name)


    # --------------------------- 
    # Set Up and Tear Down stuff
    # --------------------------- 

    @classmethod
    def setUpClass(cls):
        cls.set_up_class()

    @classmethod
    def tearDownClass(cls):
        cls.tear_down_class()

    def setUp(self):
        self.set_up()

    def tearDown(self):
        self.tear_down()

    @classmethod
    def set_up_class(cls):
        pass

    @classmethod
    def tear_down_class(cls):
        pass


    def set_up(self):
        pass

    def tear_down(self):
        pass
