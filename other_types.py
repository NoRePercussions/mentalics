import token
import typing as t
from dataclasses import dataclass

from cfanalyzer.nscoding import NSCoding


@dataclass
class Ignore(NSCoding):
    def __init_from_archive__(self, decoder) -> "NSCoding":
        return self.__init__()

    def encode_archive(self, coder) -> None:
        pass
