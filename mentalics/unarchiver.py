import typing as t
import plistlib as pl
from collections import deque
from copy import copy
from functools import wraps
from queue import Queue
from warnings import warn

from .ns_keyed_archive import NSKeyedArchive
from .ns_types import NS_TYPES
from .nscoding import NSCoding

NULL_UID = pl.UID(0)
ARCHIVE_VERSION = 100_000


class Unarchiver:
    """
    Unarchives NSKeyedArchiver plist files
    given a description of the objects contained.

    ```
    with open("my.plist", "rb") as file:
        unarchiver = Unarchiver(file)

    unarchiver.decode()
    ```
    """

    _archive: NSKeyedArchive
    _objects: dict[pl.UID, NSCoding]
    _class_map: dict[str, type[NSCoding]]

    _current_container_stack: deque[dict[str, t.Any]]
    _keys_to_decode_stack: deque[set[str]]
    _decode_later_queue: deque[tuple[dict, NSCoding]]

    _error_on_ignored_attributes: bool

    @property
    def _at_top_level(self):
        # if the stack is only the top container
        # then we are at the top
        return len(self._current_container_stack) == 1

    @property
    def _current_container(self) -> dict[str, t.Any]:
        return self._current_container_stack[-1]

    @property
    def _current_undecoded_keys(self) -> set[str]:
        return self._keys_to_decode_stack[-1]

    @_current_undecoded_keys.setter
    def _current_undecoded_keys(self, value) -> None:
        self._keys_to_decode_stack[-1] = value

    def __init__(self, fp: t.IO, class_map: t.Optional[dict[str, type[NSCoding]]] = None,
                 error_on_ignored_attributes: bool = True):
        self._archive = NSKeyedArchive(fp)
        assert self._archive.version == ARCHIVE_VERSION
        self._objects = {}
        self._class_map = class_map if class_map is not None else copy(NS_TYPES)

        self._current_container_stack = deque()
        self._keys_to_decode_stack = deque()
        self._push_container(self._archive.top)

        self._decode_later_queue = deque()

        self._error_on_ignored_attributes = error_on_ignored_attributes

    def decode(self, key: t.Optional[str] = None):
        container = self._current_container

        if key:
            key = self._sanitize_key(key)

        if key is None:
            if self._at_top_level:
                key = "root"
            else:
                raise ValueError("A key must be specified when decoding attributes of an object")

        if key not in container:
            raise ValueError(f"Key {key} not found on the current object")

        self._current_undecoded_keys = self._current_undecoded_keys.difference({key})

        archived_obj = container[key]

        obj = self._decode(archived_obj)
        self._finish_decoding()
        return obj

    def _decode(self, archived_object: t.Any):
        # A separate class so it can be called recursively when decoding a list
        if not isinstance(archived_object, pl.UID):  # NOT a reference: some pre-determined type
            return self._decode_non_reference(archived_object)
        else:
            return self._decode_reference(archived_object)

    def _decode_non_reference(self, archived_object: t.Any):
        if isinstance(archived_object, list):
            return [self._decode(o) for o in archived_object]

        return archived_object

    def _decode_reference(self, ref: pl.UID):
        """
        Take a reference to another object (a UID) and return
        the appropriate type
        """
        if ref == NULL_UID:
            return None

        if ref in self._objects:
            return self._objects[ref]

        archived_object = self._archive.objects[ref]

        if self._is_class(archived_object):
            raise ValueError("Cannot deserialize a class as an object")

        if self._is_instance(archived_object):
            # Make an instance of the class, and decode it later
            cls = self._class_of(archived_object)
            obj = cls.__new__(cls)  # We don't initialize because it may have circular references
            self._objects[ref] = obj
            self._decode_later(archived_object, obj)
            return obj

        # Otherwise, it is instantiated by plistlib
        return archived_object

    @staticmethod
    def _sanitize_key(key: str) -> str:
        """
        NSKeyedArchiver's metadata keys start with $
        and we mustn't collide with them
        """
        if key.startswith("$"):
            return "$" + key
        return key

    @staticmethod
    def _unsanitize_key(key: str) -> str:
        """
        Inverse of NSKeyedUnarchiver._sanitize_key
        """
        if key.startswith("$"):
            return key[1:]
        return key

    @staticmethod
    def _is_key_internal(key: str) -> bool:
        return len(key) >= 2 and key[0] == "$" and key[1] != "$"

    @staticmethod
    def _is_class(archived_object: t.Any):
        return isinstance(archived_object, dict) and "$classname" in archived_object

    @staticmethod
    def _is_instance(archived_object: t.Any):
        return isinstance(archived_object, dict) and "$class" in archived_object

    def _class_of(self, archived_instance: dict):
        assert self._is_instance(archived_instance)
        archived_class_ref = archived_instance["$class"]
        archived_class = self._archive.objects[archived_class_ref]
        assert self._is_class(archived_class)
        class_name = archived_class["$classname"]

        if class_name == "NSValue":
            class_name = self._special_class_of_nsvalue(archived_instance)

        if class_name not in self._class_map:
            raise ValueError(f"Class {class_name} not set on unarchiver")

        return self._class_map[class_name]

    def _special_class_of_nsvalue(self, archived_instance: dict) -> str:
        """
        For compatibility reasons, Obj-C struct types like NSPoint
        are archived as "special" NSValues. In order to provide a
        more natural interface here, we look them up specially.
        """
        special = archived_instance["NS.special"]

        special_class_names = {
            0: "NSValue",
            1: "NSPoint",
            2: "NSSize",
            # other types?
            }

        return special_class_names[special]

    def _decode_later(self, archived_obj: dict, obj: NSCoding):
        self._decode_later_queue.append((archived_obj, obj))

    def _push_container(self, container: dict):
        self._current_container_stack.append(container)
        # We also want to track what keys need to be decoded,
        # so we can give appropriate warnings when keys are
        # forgotten
        self._keys_to_decode_stack.append(self._keys_to_decode(container))

    def _pop_container(self) -> dict:
        if self._error_on_ignored_attributes and self._current_undecoded_keys:
            cls = self._class_of(self._current_container)
            raise ValueError(f"Keywords of {cls} not decoded: {self._current_undecoded_keys}. Disable with error_on_ignored_attributes=False")

        self._keys_to_decode_stack.pop()
        return self._current_container_stack.pop()

    def _keys_to_decode(self, container: dict) -> set[str]:
        all_keys = set(container.keys())
        return {self._unsanitize_key(k) for k in all_keys if not self._is_key_internal(k)}

    def _finish_decoding(self) -> None:
        """
        During decoding of one object, the unarchiver
        records a series of other objects that need to
        be decoded. This must be doable in arbitrary order
        to avoid issues with circular references. This
        method reads the list of objects to decode and
        decodes all of them.
        """

        while self._decode_later_queue:  # is not empty
            archived_obj, obj = self._decode_later_queue.popleft()

            # We need to note whatever container
            # is currently being de-archived so
            # that we know where to look for keys
            self._push_container(archived_obj)
            obj.__init_from_archive__(self)
            self._pop_container()

    def set_class(self, cls: type[NSCoding], name: str):
        self._class_map[name] = cls
