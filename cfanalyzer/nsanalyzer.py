import typing as t
import plistlib as pl
from dataclasses import dataclass
from queue import Queue



class ArchivedData:
    version: int
    objects: dict[pl.UID, t.Any]
    root: pl.UID

    def __init__(self, fp: t.IO):
        as_dict = pl.load(fp)
        self.version = as_dict["$version"]
        self.root = as_dict["$top"]["root"]

        objects = as_dict["$objects"]
        self.objects = {pl.UID(i): o for i, o in enumerate(objects)}


class ClassDefinition:
    hierarchy: list
    name: str

    def __init__(self, archived_data: dict):
        self.hierarchy = archived_data["$classes"]
        self.name = archived_data["$classname"]


class InferredClass:
    name: str

    superclass: t.Optional["InferredClass"]

    attrs: t.Optional[set[str]]
    final_attrs: t.Optional[set[str]]

    def __init__(self, name: str, superclass: t.Optional["InferredClass"], final_attrs: t.Optional[set[str]] = None):
        self.name = name
        self.superclass = superclass
        self.attrs = None
        self.final_attrs = final_attrs



class NSAnalyzer:
    """
    Takes an unknown NSKeyedArchiver plist
    and analyzes its components
    """

    _classes: dict[str, ]
    _UID_map: dict[int, ]

    def __init__(self, fp: t.IO):
        data = ArchivedData(fp)
        self._find_classes(data)

    def _find_classes(self, data: ArchivedData):
        # We want to find all classes.
        # We can start at the root object
        # and explore pl.UIDs.

        instances: dict[pl.UID, list[pl.UID]] = {}

        for uid, entry in data.objects.items():
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

        classes: dict[pl.UID, InferredClass] = {}

        for cls_uid, instance_uids in instances.items():
            cls_archived = data.objects[cls_uid]
            for uid in instance_uids:
                instance_archived: dict = data.objects[uid]
                attrs = instance_archived.keys()
                attrs = filter(lambda a: not a.startswith("$"), attrs)

                assert cls_archived["$classes"][0] == cls_archived["$classname"]

                parent_class_names = cls_archived["$classes"][:-1]
                parent_class_names_top_down = parent_class_names[::-1]

                last_class: t.Optional[InferredClass] = None
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


        pass  # debug point










