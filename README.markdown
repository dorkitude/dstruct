Background
==========

You can use DStruct to wrap a dictionary and/or a list of keyword args with an
object capable of direct attribute access.  This is great for making fake
objects that conform to a simple attribute interface.


For example, your controller can use DStruct instead of Dictionaries to pass
complex/multi-level stuff into a template.  If you pass complex stuff in with
DStruct, you've now established a flexible accessor interface, the internal
implementation of which can be changed later without consumption code being
updated.

But more than just a temporary solution for protoypes, DSTruct makes an excellent 
base model class for all of your non-db-backed models (or mock-db-backed models).  
When you extend DStruct, you can apply schema rules that range in rigidity from
anarchist to fascist.


General Examples
----------------

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

You can subclass DStruct to configure its behavior.  

 * You can specify certain attributes as "required", and if your call to the
constructor is missing one of them, initialization will raise an Exception
of the type `DStruct.RequiredAttributeMissing`.

 * Optionally, you can demand a specific type for each of these attributes.  If
such an attribute is present, but its value is of an invalid type, `__init__`
will raise a `DStruct.RequiredAttributeInvalid` Exception.

 * You can also tell DStruct not to automatically verify your schema by
settings the class attribute `struct_schema_check_on_init` to `False`.  This
is useful in cases where some of the required values are derived, so they
can't all be passed into the constructor.  See the test
`test_delayed_verification()` for an example of this.

 * Finally, you can make the schema less rigid by overriding
`cls.get_extra_allowed_types()` -- for instance, you might want to allow
`unicode` values and `str` to be interchangeable.  See the test
`test_flexible_schema()` for an example of this.


Basic Subclass Examples: RequiredAttribute
-------------------------------------------

Declare a subclass with some required attributes:

    class CartesianCoordinate(DStruct):
        """
        Represents a cartesian point.
        You must construct me with 'x' and 'y' attibutes!
        """

        x = DStruct.RequiredAttribute()
        y = DStruct.RequiredAttribute()

        # FYI, it would be equivalent to write:
        # required_attributes = {"x":None, "y":None}

Valid use:

    origin = CartesianCoordinate(x=0, y=0)
    point = CartesianCoordinate(x=5, y=12)
    point.x - origin.x # outputs 5
    point.y - origin.y # outputs 12

Invalid use:
    
    crap = CartesianCoordinate(x=3) # raises RequiredAttributeMissing


Advanced Subclass Examples: RequiredAttribute with a type constraint
---------------------------------------------------------------------

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

    with self.assert_raises(DStruct.RequiredAttributeInvalid):
        thing = MapLocation({
            "latitude": 1.5,
            "longitude": 3,  # this is an int, not a float!  BOOM!
            "label": Label("sup"), 
            })


    with self.assert_raises(DStruct.RequiredAttributeInvalid):
        thing = MapLocation({
            "latitude": 1.5,
            "longitude": 3.4, 
            "label": 991,# this is an int, not a Label instance!  BOOM!
            })
