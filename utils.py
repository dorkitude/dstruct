import string


def dedupe_list(input_list, preserve_order=True):
    """

    Remove duplicates from the list, preserving order.

    :param input_list: list, the thing we need to dedupe
    :returns: list, a new copy of the input_list without duplicates

    """
    seen = set()
    return [ x for x in input_list if x not in seen and not seen.add(x)]


def snake_to_mixed(underscore_input):
    """
    mixedCaseLooksLikeThis
    """

    word_list = underscore_input.split('_')
    word_count = len( word_list )
    if word_count > 1:
        for i in range(1, word_count):
            word_list[i] = string.capwords( word_list[i] )
    ret = ''.join(word_list)
    return ret



def extract_classes(clazz):
    """

    Find all parent classes, anywhere in the inheritance tree.

    :param clazz: class, the thing to crawl through 
    
    Returns a list of all base classes in the inheritance tree

    """

    extracted = [clazz]

    for base in clazz.__bases__:
        extracted += extract_classes(base)

    # no need to include 'object'
    if object in extracted:
        extracted.remove(object)

    return dedupe_list(extracted, preserve_order=True)
 

# Decorate a method with @classproperty to make it behave like @property, but 
# at the class level. 
# Stolen by dorkitude from StackOverflow: http://goo.gl/06cij

class ClassPropertyError(Exception):
    pass


class ClassPropertyDescriptor(object):

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)

    return ClassPropertyDescriptor(func)

