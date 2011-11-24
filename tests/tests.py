# Python standard library imports:
import random
import unittest

# Our imports:
from ..dorkitude_utils.base_test_case import BaseTestCase

from .. import DStruct


class DStructTestCase(BaseTestCase):

    def test_struct(self):

        # test constructing with a dict
        s = DStruct({"k1":"v1", "k2": "v2"})
        self.assert_equal(s.k1, "v1")
        self.assert_equal(s.k2, "v2")

        # test constructing with a list of keyword args
        s = DStruct(k1="v1", k2="v2")
        self.assert_equal(s.k1, "v1")
        self.assert_equal(s.k2, "v2")
        
        # test constructing with both 
        s = DStruct({"k3":"v3"}, k1="v1", k2="v2")
        self.assert_equal(s.k1, "v1")
        self.assert_equal(s.k2, "v2")
        self.assert_equal(s.k3, "v3")

        # confirm readability as dict
        self.assert_equal(s["k1"], "v1")
        self.assert_equal(s["k2"], "v2")
        self.assert_equal(s["k3"], "v3")

    def test_struct_required_attribute_missing(self):

        # make a custom struct class:
        class CartesianCoordinate(DStruct):
            '''

            Represents a cartesian point.  You must construct with 'x' and 'y'
            attibutes!

            '''

            x = DStruct.RequiredAttribute()
            y = DStruct.RequiredAttribute()

            # FYI, it would be equivalent to write:
            # required_attributes = {"x":None, "y":None}


        # create a couple of coordinates:
        origin = CartesianCoordinate({"x":0, "y":0})
        point = CartesianCoordinate(x=5, y=12)
        
        # confirm their values were stored appropriately:
        self.assert_equal(point.x - origin.x, 5) # outputs 5
        self.assert_equal(point.y - origin.y, 12) # outputs 5
        
        # test a few varieties of improper use:
        with self.assertRaises(DStruct.RequiredAttributeMissing):
            crap = CartesianCoordinate(x=3)

        with self.assertRaises(DStruct.RequiredAttributeMissing):
            crap = CartesianCoordinate({"y":3})

        with self.assertRaises(DStruct.RequiredAttributeMissing):
            crap = CartesianCoordinate()


    def test_flexible_schema(self):

        class HippieStruct(DStruct):

            x = DStruct.RequiredAttribute(int)
            y = DStruct.RequiredAttribute(float)

            @classmethod
            def get_extra_allowed_types(cls, _type):
                x = super(HippieStruct, cls).get_extra_allowed_types(
                        _type)

                if _type is int:
                    x.append(float)
                elif _type is float:
                    x.append(int)

                return x


        # None of these should fail, since float and int are interchangeable
        # now:
        HippieStruct(x=1, y=1)
        HippieStruct(x=1.5, y=1.5)
        HippieStruct(x=1, y=1.5)
        HippieStruct(x=1.5, y=1)

        # But this should still fail:
        with self.assertRaises(DStruct.RequiredAttributeInvalid):
            HippieStruct(x="DUDE THAT IS A STRING!", y=1)


    def test_struct_required_attribute_invalid(self):

        class BaseLabel(object):
            def __init__(self, name):
                self.name = name
        

        class Label(BaseLabel):
            pass


        # make a custom struct class:
        class MapLocation(DStruct):
            '''

            Represents a map location, specified by floating point values.
            
            You must construct this with float values for "latitude" and
            "longitude", plus a BaseLabel value for "label".

            '''

            latitude = DStruct.RequiredAttribute(float)
            longitude = DStruct.RequiredAttribute(float)
            label = DStruct.RequiredAttribute(BaseLabel)

            @property
            def name(self):
                return self.label.name

            # FYI, it would be equivalent to write this:
                #required_attributes = {
                #        "latitude":float, 
                #        "longitude":float,
                #        "name":BaseLabel,
                #        }


        # make one with a BaseLabel instance for the "label" attribute:
        MapLocation(latitude=1.1,longitude=1.1,label=BaseLabel("hi"))
        # ...and one with a Label instance:
        MapLocation(latitude=1.1,longitude=1.1,label=Label("hi"))

        # make one with a single dictionary argument:
        coffeeshop = MapLocation({
                "latitude": 37.744861,
                "longitude": -122.477732,
                "label": Label("Brown Owl Coffee"),
                })
        # ...and confirm the values are held:
        self.assert_equal(coffeeshop.name, "Brown Owl Coffee")
        self.assert_equal(coffeeshop.longitude, -122.477732)
        self.assert_equal(coffeeshop.latitude, 37.744861)

        # make one with a number of keyword arguments:
        office = MapLocation(
                latitude=37.781586,
                longitude=-122.391343,
                label=BaseLabel("Hatchery SF"), 
                )
        # ...and confirm the values are held:
        self.assert_equal(office.name, "Hatchery SF")
        self.assert_equal(office.longitude, -122.391343)
        self.assert_equal(office.latitude, 37.781586)

        # make one with a dictionary argument AND and some keyword arguments:
        space = MapLocation(
                {"latitude":37.773564},
                longitude=-122.415869,
                label=Label("pariSoma"),
                )
        # ...and confirm the values are held:
        self.assert_equal(space.name, "pariSoma")
        self.assert_equal(space.longitude, -122.415869)
        self.assert_equal(space.latitude, 37.773564)


        # supply an invalid attribute type
        with self.assertRaises(DStruct.RequiredAttributeInvalid):
            thing = MapLocation({
                "latitude": 1.5,
                "longitude": 3,  # this is an int, not a float!  BOOM
                "label": Label("sup"), 
                })

        with self.assertRaises(DStruct.RequiredAttributeInvalid):
            thing = MapLocation({
                "latitude": 1.5,
                "longitude": 3.4, 
                "label": 991,# this is an int, not a Label instance!  BOOM
                })

        
        # confirm
        with self.assertRaises(DStruct.RequiredAttributeMissing):
            thing = MapLocation({
                "latitude": 1.5,
                "longitude": 3.4,
                # we didn't send "name", BOOM!
                })

    def test_struct_required_attribute_dictionary(self):
        """

        Make sure we can use a class-level dictionary called
        `required_attributes` rather than relying on the classproperty
        `DStruct.required_attributes()`.

        """

        class SlowInt(DStruct):
            """
            A wrapper for a primitive: the worst integer implementation either.
            """
            required_attributes = {"value": int}

        # this should work:
        i = SlowInt(value=9)

        # this should work:
        i = SlowInt({"value":9})

        # try not sending a field called "value":
        with self.assertRaises(DStruct.RequiredAttributeMissing):
            i = SlowInt({"x":9})

        # try sending an invalid type for "value":
        with self.assertRaises(DStruct.RequiredAttributeInvalid):
            i = SlowInt({"value":9.4}) # a float, not an int. BOOM!



