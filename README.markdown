General Use
===========

You can use this to wrap a dictionary and/or a list of keyword args with an
object capable of direct attribute access.  This is great for making fake
objects that conform to a simple attribute interface.

For example, your controller can use DStruct instead of Dictionaries to
pass complex/multi-level stuff into a template.  If you pass complex stuff
in with DStruct, you've established a flexible accessor interface, the
backend implementation of which can be changed later with no harm done!


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
        # You must construct with 'x' and 'y' attibutes!

        

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


Advanced Subclass Examples: Required Attribute
----------------------------------------------

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
