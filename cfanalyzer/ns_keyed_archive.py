import plistlib as pl
import typing as t
from dataclasses import dataclass

class ArchivedObject:
    uid: pl.UID

    def __init__(self, *args, uid: pl.UID, **kwargs):
        self.uid = uid
        super().__init__(*args, **kwargs)


class ArchivedInstance(ArchivedObject, dict):
    class_uid: pl.UID

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_uid = self.pop("$class")

    @staticmethod
    def is_instance(archived_obj: t.Any):
        return isinstance(archived_obj, dict)\
            and "$class" in archived_obj


class ArchivedClass(ArchivedObject, dict):
    class_name: str
    classes: list[str]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_name = self.pop("$classname")
        self.classes = self.pop("$classes")

    @staticmethod
    def is_class(archived_obj: t.Any):
        return isinstance(archived_obj, dict)\
            and "$classname" in archived_obj\
            and "$classes" in archived_obj


# Objects that can appear in
# the main NSKeyedArchiver dict
ArchiveType = t.Union[ArchivedInstance, ArchivedClass, bool, int, float, str, bytes]


class NSKeyedArchive:
    version: int
    _objects: dict[pl.UID, ArchiveType]
    _root: pl.UID

    def __init__(self, fp: t.IO):
        as_dict = pl.load(fp)
        self.version = as_dict["$version"]
        self._root = as_dict["$top"]["root"]

        objects = as_dict["$objects"]
        self._objects = {pl.UID(i): o for i, o in enumerate(objects)}

    def __getitem__(self, item: pl.UID) -> ArchiveType:
        archived_obj = self._objects[item]

        if ArchivedInstance.is_instance(archived_obj):
            return ArchivedInstance(archived_obj, uid=item)
        if ArchivedClass.is_class(archived_obj):
            return ArchivedClass(archived_obj, uid=item)

        return archived_obj

    @property
    def root(self) -> pl.UID:
        return self._root
