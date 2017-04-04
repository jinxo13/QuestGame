import importlib

class Helpers(object):
    """description of class"""
    @staticmethod
    def is_number(s):
        try:
            complex(s) # for int, long, float and complex
        except ValueError:
            return False
        return True

    @staticmethod
    def class_for_name(module_name, class_name):
        """Load class by name"""
        # load the module, will raise ImportError if module cannot be loaded
        m = importlib.import_module(module_name)
        # get the class, will raise AttributeError if class cannot be found
        c = getattr(m, class_name)
        return c

    @staticmethod
    def create_instances(cls, num):
        result = []
        for i in range(num): result.append(cls())
        return result