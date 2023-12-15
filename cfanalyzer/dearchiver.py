import typing as t
import plistlib as pl
from collections import deque
from copy import copy
from functools import wraps
from queue import Queue

from .nscoding import NSCoding
from .ns_keyed_archive import ArchivedClass, ArchivedInstance, NSKeyedArchive
from .ns_types import NS_TYPES


class Dearchiver:
    """
    De-archives NSKeyedArchiver plist files
    given a description of the objects contained.

    Takes a root object which describes a tree of objects:

    ```
    @dataclass
    class MyChild:
        name: str

    @dataclass
    class MyParent:
        child: MyChild

    dearchiver = Dearchiver(MyParent)
    ```

    Types are inferred from __init__'s signature.

    """

    _class_map: dict[str, type[NSCoding]]

    def __init__(self, class_map: dict[str, type[NSCoding]] = None):
        if class_map is None:
            self._class_map = copy(NS_TYPES)
        else:
            self._class_map = class_map

    def set_class(self, cls: type[NSCoding], coded_name: t.Optional[str] = None) -> None:
        """
        Add a class to the dearchiver.
        :param cls: The class to add
        :param coded_name: The name with which it appears in archived files
        :return:
        """
        if coded_name is None:
            coded_name = cls.__name__
        self._class_map[coded_name] = cls

    def load(self, fp: t.IO) -> NSCoding:
        archive = NSKeyedArchive(fp)

        decoder = Decoder(archive, self._class_map)
        root_obj = decoder.decode_all()
        return root_obj


class Decoder:
    """
    Directly handles dearchiving.

    It is passed around objects being dearchived
    so they can get their attributes.

    ```
    @classmethod
    def decode(archive):
        my_attr = archive.decode('myAttr')
        return MyClass(my_attr=my_attr)
    ```
    """

    _archive: NSKeyedArchive
    _class_map: dict[str, type[NSCoding]]
    _instance_objects: dict[pl.UID, NSCoding]

    _current_obj_uid: t.Optional[pl.UID]
    _to_decode: deque[pl.UID]

    def __init__(self, archive: NSKeyedArchive, class_map: dict[str, type[NSCoding]]):
        self._archive = archive
        self._class_map = class_map

        self._instance_objects = {}

        self._current_obj_uid = None
        self._to_decode = deque()

    def decode_all(self) -> NSCoding:
        self._to_decode.append(self._archive.root)

        while self._to_decode:
            to_decode = self._to_decode.popleft()
            self._decode_object(to_decode)

        return self._instance_objects[self._archive.root]

    def _decode_object(self, uid: pl.UID):
        """
        Decode an object in the archive.

        It may be:
        - An instance of a class
        - A class definition
        - An integer, float, string

        We do not expect to need to dearchive class definitions,
        so they will cause an error.
        """
        self._current_obj_uid = uid
        archived_object = self._archive[uid]

        if isinstance(archived_object, ArchivedInstance):
            obj = self._get_instance_object(archived_object)
            obj.decode_archive(self)

        elif self._is_archived_single_primitive(archived_object):
            # plutil dearchives these for us
            obj = archived_object

        elif isinstance(archived_object, ArchivedClass):
            raise ValueError(f"Cannot dearchive class definition")

        else:
            raise ValueError(f"The type seen was not expected at the archive root")

        self._current_obj_uid = None
        return obj

    def _decode_object_reference(self, uid: pl.UID):
        """
        Decode an object that is referenced by another
        object. Usually, this is a string.

        It may be:
        - An instance of a class
        - A class definition
        - An integer, float, string

        We do not expect to need to dearchive class definitions,
        so they will cause an error.
        """
        archived_object = self._archive[uid]

        if isinstance(archived_object, ArchivedInstance):
            obj = self._get_instance_object(archived_object)
            return obj

        if isinstance(archived_object, ArchivedClass):
            raise ValueError(f"Cannot dearchive class definition")

        if self._is_archived_single_primitive(archived_object):
            # plutil dearchives these for us
            return archived_object

        raise ValueError(f"The type seen was not expected")

    def _get_instance_object(self, archived_object: ArchivedInstance) -> NSCoding:
        if archived_object.uid in self._instance_objects:
            return self._instance_objects[archived_object.uid]

        # We haven't seen this object yet: we must create it.
        # We don't initialize it, because it will be initialized
        # when it gets dearchived later.

        cls = self._get_class(archived_object)
        obj = cls.__new__(cls)

        self._to_decode.append(archived_object.uid)
        self._instance_objects[archived_object.uid] = obj
        self._to_decode.append(archived_object.uid)

        return obj

    def _get_class(self, archived_instance: ArchivedInstance) -> type[NSCoding]:
        class_uid = archived_instance.class_uid
        archived_class: ArchivedClass = self._archive[class_uid]
        class_name = archived_class.class_name

        if class_name not in self._class_map:
            raise ValueError(f"Class {class_name} not set on dearchiver")

        return self._class_map[class_name]

    def _is_archived_single_primitive(self, obj: t.Any) -> bool:
        return isinstance(obj, bool) \
            or isinstance(obj, int) \
            or isinstance(obj, float) \
            or isinstance(obj, str) \
            or isinstance(obj, bytes)

    def decode(self, key_name: str):
        """
        Called by objects to dearchive their attributes:

        ```
        @classmethod
        def decode(archive):
            my_attr = archive.decode('myAttr')
            return MyClass(my_attr=my_attr)
        ```
        """
        assert self._current_obj_uid is not None
        attr = self._archive._objects[self._current_obj_uid][key_name]

        return self._decode_attribute(attr)

    def _decode_attribute(self, archive: t.Any) -> t.Any:
        if isinstance(archive, pl.UID):
            uid = archive
            return self._decode_object_reference(uid)

        if isinstance(archive, list):
            # Fixme: if we return an UnresolvedNSCoding in a list,
            # it won't be seen by NSCoding's getattribute, and never
            # gets resolved into an NSCoding. Thus we probably need a
            # helper class here.
            return [self._decode_attribute(elem) for elem in archive]

        if self._is_archived_single_primitive(archive):
            # Already dearchived by plutil
            return archive

        raise ValueError(f"Type of archive not known")


