import token
import typing as t
from dataclasses import dataclass

from cfanalyzer.nscoding import NSCoding


@dataclass
class Ignore(NSCoding):
    @classmethod
    def decode_archive(cls, dearchiver) -> "NSCoding":
        return cls()

    def encode_archive(self, archiver) -> None:
        pass
