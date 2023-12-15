import typing as t
import plistlib as pl
from copy import copy
from dataclasses import dataclass
from queue import Queue

from .ns_keyed_archive import NSKeyedArchive


class InferredClass:
    name: str

    superclass: t.Optional["InferredClass"]
    subclasses: list["InferredClass"]

    attrs: t.Optional[set[str]]
    final_attrs: t.Optional[set[str]]

    def __init__(self, name: str, superclass: t.Optional["InferredClass"], final_attrs: t.Optional[set[str]] = None):
        self.name = name
        self.superclass = superclass
        self.subclasses = []
        self.attrs = None
        self.final_attrs = final_attrs

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.class_name

    def __repr__(self):
        return f"<InferredClass {self.name}>"



class Explorer:
    """
    Takes an unknown NSKeyedArchiver plist
    and analyzes its components
    """

    _classes: dict[str, InferredClass]
    _UID_map: dict[int, ]

    def __init__(self, fp: t.IO):
        data = NSKeyedArchive(fp)
        self._classes = self._find_classes(data)

    def _find_classes(self, data: NSKeyedArchive):
        # We want to find all classes.
        # We can start at the root object
        # and explore pl.UIDs.

        instances: dict[pl.UID, list[pl.UID]] = {}

        for uid, entry in data._objects.items():
            if isinstance(entry, dict) and "$class" in entry:  # a class instance
                defintion_uid = entry["$class"]

                if defintion_uid not in instances:
                    instances[defintion_uid] = []

                instances[defintion_uid].append(uid)

        # instances is now a mapping of classes to all their instances
        # We can use this to build a map of the attributes of each class
        # and infer their types.
        # Then we can use each class and the hierarchy table
        # to infer parent classes.

        classes: dict[str, InferredClass] = {}

        universal_class = InferredClass("$Object", None)
        classes["$Object"] = universal_class

        for cls_uid, instance_uids in instances.items():
            cls_archived = data._objects[cls_uid]
            for uid in instance_uids:
                instance_archived: dict = data._objects[uid]
                attrs = instance_archived.keys()
                attrs = filter(lambda a: not a.startswith("$"), attrs)

                assert cls_archived["$classes"][0] == cls_archived["$classname"]

                parent_class_names = cls_archived["$classes"][:-1]
                parent_class_names_top_down = parent_class_names[::-1]

                last_class: t.Optional[InferredClass] = universal_class
                for class_name in parent_class_names_top_down:
                    # If we haven't recorded this class yet, do so
                    if class_name not in classes:
                        cls = InferredClass(
                            name=class_name,
                            superclass=last_class
                            )
                        classes[class_name] = cls
                    else:
                        cls = classes[class_name]

                    if cls not in last_class.subclasses:
                        last_class.subclasses.append(cls)
                    last_class = cls

                # Now, we need to look at our resultant class

                class_name = cls_archived["$classname"]
                if class_name not in classes:
                    cls = InferredClass(
                        name=class_name,
                        superclass=last_class,
                        final_attrs=set(attrs),
                        )
                    classes[class_name] = cls
                else:
                    # This end class was already created
                    cls = classes[class_name]
                    if cls.final_attrs is None:
                        # Created as a parent of another class
                        cls.final_attrs = set(attrs)
                    else:
                        # Created as an end class
                        if class_name == "NSValue":
                            # NSValue is very annoying
                            # and doesn't always serialize to the
                            # same attributes. So it needs
                            # special handling.
                            pass  # fixme: diversification of NSValues
                        else:
                            # Sanity check attributes
                            assert cls.final_attrs == set(attrs)

        # We have a list of classes and their final attributes
        # Now we need to find all classes with the same superclass
        # and take the intersection of their attributes to find
        # superclass attributes.

        # This might not always work: e.g. if the class hierarchy
        # is NSObject > NSDictionary > NSMutableDictionary
        # and no other objects are used, all attributes of
        # NSMutableDictionary will be assigned to NSObject.

        self._infer_attrs(universal_class)

        return classes

    def _infer_attrs(self, cls: t.Optional[InferredClass]):
        # We want to take all the final attributes that each class has
        # and walk up the inheritance tree to infer what attrs each
        # parent class has.

        # We are visiting each class for the first time.
        # Setting attrs marks it as visited
        cls.attrs = set()

        # Find all attribute sets of children...
        all_subclass_attrs: list[set] = []
        for subclass in cls.subclasses:
            if subclass.attrs is None:
                self._infer_attrs(subclass)
            all_subclass_attrs.append(subclass.attrs)

        # ...then intersect them if there are any children,
        # or else say no mutual attributes
        if len(all_subclass_attrs) > 0:
            mutual_attrs = set.intersection(*all_subclass_attrs)
        else:
            mutual_attrs = set()

        mutual_attrs: set
        final_attrs: set = cls.final_attrs or set()

        for subclass in cls.subclasses:
            # Inferred attrs should be a member of all
            # child classes
            assert subclass.attrs.issuperset(mutual_attrs)
            subclass.attrs.difference_update(mutual_attrs)

            # Other attrs on the parent class should not
            # appear in its children
            assert len(subclass.attrs.intersection(final_attrs)) == 0

        # Add mutual and final attributes to class
        cls.attrs = mutual_attrs.union(final_attrs)

    def _into_objects(self, data: NSKeyedArchive):
        # We have a description of classes:
        # now we need to walk through the data
        # and turn it into those classes.
        #
        # Probably going to rely on Dearchiver

        pass













