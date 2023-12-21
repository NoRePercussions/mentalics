import plistlib as pl
import typing as t
from dataclasses import dataclass


class NSKeyedArchive:
    version: int
    objects: dict[pl.UID, t.Any]
    top: dict[str, pl.UID]

    def __init__(self, fp: t.IO):
        as_dict = pl.load(fp)
        self.version = as_dict["$version"]
        self.top = as_dict["$top"]

        objects = as_dict["$objects"]
        self.objects = {pl.UID(i): o for i, o in enumerate(objects)}
