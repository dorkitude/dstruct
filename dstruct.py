from utils import classproperty, extract_classes

class DStruct(object):
    """

    You can use this to wrap a dictionary and/or a list of keyword args with an
    object capable of direct attribute access.  This is great for making fake
    objects that conform to a simple attribute interface.
    
    For example, your controller can use DStruct instead of Dictionaries to
    pass complex/multi-level stuff into a template.  If you pass complex stuff
    in with DStruct, you've established a flexible accessor interface, the
    backend implementation of which can be changed later with no harm done!

    Simple Usage
    ============

    Initialize with a dictionary:

        struct = DStruct({"k1":"v1", "k2": "v2"})
        struct.k1 # outputs "v1"

    Initialize with keyword arguments:

        struct = DStruct(k1="v1", k2="v2")
        struct.k1 # outputs "v1"

    Initialize with a dictionary *and* keyword arguments:

        struct = DStruct({"k3":"v3"}, k1="v1", k2="v2")
        struct.k3 # outputs "v3"
        struct.k2 # outputs "v2"


    Subclassing
    ===========

    You can also subclass DStruct to configure certain behavior.

    You can specify certain attributes as "required", and if your call to the
    constructor is missing one of them, initialization will raise an Exception
    of the type `RequiredAttributeMissing`.

    Optionally, you can demand a specific type for each of these attributes.


    Basic Subclass Examples: Required Attribute
    -------------------------------------------

    Declare a subclass with some required attributes:
    
        class CartesianCoordinate(DStruct):
            # Represents a cartesian point.
            
            # You must construct this with 'x' and 'y' attributes:
            x = DStruct.RequiredAttribute()
            y = DStruct.RequiredAttribute()

    Valid use:

        origin = CartesianCoordinate(x=0, y=0)
        point = CartesianCoordinate(x=5, y=12)
        point.x - origin.x # outputs 5
        point.y - origin.y # outputs 12

    Invalid use:
        
        crap = CartesianCoordinate(x=3) # raises RequiredAttributeMissing

    Advanced Subclass Examples: Required Attribute with a type
    ----------------------------------------------------------
    
    Declare a DStruct subclass with some attribute type requirements:

        class Label(object):
            pass

        class MapLocation(DStruct):
            latitude = DStruct.RequiredAttribute(float)
            longitude = DStruct.RequiredAttribute(float)
            label = DStruct.RequiredAttribute(Label)

            @property
            def name(self):
                return self.label.name
        
    Valid use:

        l1 = MapLocation(latitude=1.1,longitude=1.1,label=BaseLabel("hi"))
        l2 = MapLocation(latitude=1.1,longitude=1.1,label=Label("hi"))

    Invalid use:

        # raises an RequiredAttributeInvalid
        thing = MapLocation({
            "latitude": 1.5,
            "longitude": 3,  # this is an int, not a float!  BOOM!
            "label": Label("sup"), 
            })
            
        # raises an RequiredAttributeInvalid
        thing = MapLocation({
            "latitude": 1.5,
            "longitude": 3.4, 
            "label": 991,  # this is an int, not a Label instance!  BOOM!
            })

    """

    @classproperty
    def struct_schema_check_on_init(cls):
        """

        :returns: Boolean.  If True, the `__init__` method will call the
        `check_struct_schema` method at the end. 

        """
        return True


    def __init__(self, input_dict=None, **entries): 
        """

        Load the provided inputs onto this object, then set the instance
        attribute `_struct_has_loaded` to True.  Optionally (if the class
        attribute `struct_schema_check_on_init` is True), end with a call to
        `self.check_struct_schema()`.

        :param input_dict:  Dictionary.  Any number of key-value pairs to be
        loaded onto this instance.

        :param **entries:  Any number of key-value pairs to be loaded onto this
        instance.

        :returns: None

        """

        # 1. Load the stuff:
        self.load_struct_inputs(input_dict, **entries)

        # 2. Mark myself as having been loaded:
        self._struct_has_loaded = True

        # 3. Optionally, end with a schema check:
        if self.__class__.struct_schema_check_on_init:
            self.check_struct_schema()

    def load_struct_inputs(self, input_dict, **entries):

        if not input_dict:
            input_dict = {}

        self.__dict__.update(input_dict)
        self.__dict__.update(entries)

    @classmethod
    def get_extra_allowed_types(cls, _type):
        """

        Get a list of other types that are "squint matches" for the specified
        type.

        Subclasses can override this for more flexible schemas!

        :param _type:  Type.  The type that was specified in the
        `RequiredAttribute` constructor (the schema's expected type).

        :returns:  List of Types.

        """

        extra_types = []

        # This is provided largely as an example, but also because it's likely
        # to be the desired behavior for most people using `str` as a required
        # type:
        if _type is str:
            extra_types.append(unicode)
        elif _type is unicode:
            extra_types.append(str)

        return extra_types



    def check_struct_schema(self, clazz=None):
        """

        Check this instance's properties against the class's requirements.

        If a required attribute is missing, raise a RequiredAttributeMissing.

        If a required attribute is present, but has an unacceptable type,
        raise a RequiredAttributeInvalid.

        :param clazz: Class.  From which class should we pull the schema?
        Defaults to the instance's class (i.e. `self.__class`), which would
        confirm all the required attributes in the inheritance tree.  This
        parameter is exposed so a subclasses can check the relevant schemas
        with more granularity, if desired.

        :returns:  None.

        """

        if not clazz:
            clazz = self.__class__

        # are there any required attributes?
        if len(clazz.required_attributes) > 0:
            # ...if so, confirm them all:
            for key,required_type in clazz.required_attributes.items():

                # confirm I have something stored at this key
                if key not in self.__dict__:
                    raise DStruct.RequiredAttributeMissing(self, key)

                # validate my value's type (if one is specified)
                if required_type:

                    allowed_types = [required_type]
                    allowed_types += clazz.get_extra_allowed_types(
                            required_type)
                
                    if not [1 for allowed_type in allowed_types 
                            if isinstance(self.__dict__[key], allowed_type)]:
                        raise DStruct.RequiredAttributeInvalid(
                                self, key, self.__dict__[key])

    def __getitem__(self, key):
        return self.__dict__[key]

    @classproperty
    def required_attributes(cls):
        """

        Figures out which attributes, if any, were declared as
        RequiredAttribute instances.

        :returns: Dictionary.  The keys in this dictionary are the names of the
        attributes that are required.  For each attribute, the value either
        `None` or a type object.

        """

        required_attributes = {}

        for clazz in extract_classes(cls):
            for key,value in clazz.__dict__.items():
                if isinstance(value, cls.RequiredAttribute):
                    required_attributes[key] = value.required_type

        return required_attributes

    class RequiredAttribute(object):
        """

        This is a declarative marker class.
        
        It can be used by subclasses to declare a specific attribute as
        a required attribute.

        If it does so, initialization will fail with a
        `RequiredAttributeMissing` exception.

        """
        def __init__(self, required_type=None):
            self.required_type = required_type


    class RequiredAttributeMissing(Exception):
        """

        This is raised by `DStruct.__init__` if you didn't construct the
        instance with some attribute that has been designated as a required
        attribute.

        """
        def __init__(self, struct_instance, key):
            msg = "You need an attribute called `{}` when making a {}".format(
                    key, struct_instance.__class__.__name__)
            super(self.__class__, self).__init__(msg)


    class RequiredAttributeInvalid(Exception): 
        """

        This is raised by `DStruct.__init__` if you construct the instance
        with a required attribute that isn't an instance of the specified type. 

        """
        def __init__(self, struct_instance, key, value):
            msg = "The value of the attribute`{}` must be an instance of {}.".format(
                    key, struct_instance.__class__.required_attributes[key])
            msg += "  Instead, I got: {}, which is a {}".format(
                    value, type(value))
            super(self.__class__, self).__init__(msg)
