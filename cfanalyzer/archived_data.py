import plistlib as pl
import typing as t


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
