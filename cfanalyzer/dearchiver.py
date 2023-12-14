import typing as t
import plistlib as pl
from collections import deque
from copy import copy
from functools import wraps
from queue import Queue

from .nscoding import NSCoding
from .archived_data import ArchivedData
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

    def get_object(self, uid: pl.UID) -> NSCoding:
        return self._objects[uid]

    def load(self, fp: t.IO) -> NSCoding:
        data = ArchivedData(fp)

        decoder = Decoder(data, self._class_map)
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

    _data: ArchivedData
    _class_map: dict[str, type[NSCoding]]
    _objects: dict[pl.UID, NSCoding]

    _current_obj_uid: t.Optional[pl.UID]
    _to_decode: deque[pl.UID]

    def __init__(self, data: ArchivedData, class_map: dict[str, type[NSCoding]]):
        self._data = data
        self._class_map = class_map

        self._objects = {}

        self._current_obj_uid = None
        self._to_decode = deque()

    def decode_all(self) -> NSCoding:
        root_uid = self._data.root
        self._to_decode.append(root_uid)

        while self._to_decode:
            uid = self._to_decode.popleft()
            self._decode_object(uid)

        return self._objects[root_uid]

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
        archived_object = self._data.objects[uid]

        if self._is_archived_instance(archived_object):
            # Get the (uninitialized) object or create and store a new one
            cls = self._get_class_of_archived_instance(archived_object)
            obj = self._objects.setdefault(uid, cls.__new__(cls))

            return obj

        elif self._is_archived_single_primitive(archived_object):
            # plutil dearchives these for us
            obj = archived_object

        elif self._is_archived_class_definition(archived_object):
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
        archived_object = self._data.objects[uid]

        if self._is_archived_instance(archived_object):
            # Get the (uninitialized) object or create and store a new one
            cls = self._get_class_of_archived_instance(archived_object)
            obj = self._objects.setdefault(uid, cls.__new__(cls))

            # Will be initialized when visited later
            self._to_decode.append(uid)
            return obj

        if self._is_archived_single_primitive(archived_object):
            # plutil dearchives these for us
            return archived_object

        if self._is_archived_class_definition(archived_object):
            raise ValueError(f"Cannot dearchive class definition")

        raise ValueError(f"The type seen was not expected")


    def _get_class_of_archived_instance(self, obj: dict) -> type[NSCoding]:
        class_uid = obj["$class"]
        class_name = self._data.objects[class_uid]["$classname"]

        if class_name not in self._class_map:
            raise ValueError(f"Class {class_name} not set on dearchiver")

        return self._class_map[class_name]

    def _is_archived_instance(self, obj: t.Any) -> bool:
        return isinstance(obj, dict) and "$class" in obj

    def _is_archived_reference(self, obj: t.Any) -> bool:
        return isinstance(obj, pl.UID)

    def _is_archived_class_definition(self, obj: t.Any) -> bool:
        return isinstance(obj, dict) and "$classname" in obj

    def _is_archived_int(self, obj: t.Any) -> bool:
        return isinstance(obj, int)

    def _is_archived_float(self, obj: t.Any) -> bool:
        return isinstance(obj, float)

    def _is_archived_str(self, obj: t.Any) -> bool:
        return isinstance(obj, str)

    def _is_archived_bytes(self, obj: t.Any) -> bool:
        return isinstance(obj, bytes)

    def _is_archived_list(self, obj: t.Any) -> bool:
        return isinstance(obj, list)

    def _is_archived_dict(self, obj: t.Any) -> bool:
        return isinstance(obj, dict)\
            and not self._is_archived_instance(obj)\
            and not self._is_archived_class_definition(obj)

    def _is_archived_single_primitive(self, obj: t.Any) -> bool:
        return self._is_archived_list(obj) \
            or self._is_archived_dict(obj) \
            or self._is_archived_int(obj) \
            or self._is_archived_float(obj) \
            or self._is_archived_str(obj) \
            or self._is_archived_bytes(obj)

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
        attr = self._data.objects[self._current_obj_uid][key_name]

        return self._decode_attribute(attr)

    def _decode_attribute(self, archive: t.Any) -> t.Any:
        if self._is_archived_reference(archive):
            uid = archive
            return self._decode_object_reference(uid)

        if self._is_archived_list(archive):
            # Fixme: if we return an UnresolvedNSCoding in a list,
            # it won't be seen by NSCoding's getattribute, and never
            # gets resolved into an NSCoding. Thus we probably need a
            # helper class here.
            return [self._decode_attribute(elem) for elem in archive]

        if self._is_archived_single_primitive(archive):
            # Already dearchived by plutil
            return archive

        raise ValueError(f"Type of archive not known")


