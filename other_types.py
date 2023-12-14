import token
import typing as t
from dataclasses import dataclass

from cfanalyzer.nscoding import NSCoding


@dataclass
class Ignore(NSCoding):
    def decode_archive(self, dearchiver) -> "NSCoding":
        return self.__init__()

    def encode_archive(self, archiver) -> None:
        pass
