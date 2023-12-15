from dataclasses import dataclass

from ..nscoding import NSCoding


@dataclass
class NSData(NSCoding):
    data: bytes

    def __init_from_archive__(self, decoder) -> "NSCoding":
        data: bytes = decoder.decode("NS.data")
        return self.__init__(data)

    def encode_archive(self, coder) -> None:
        pass

    def __bytes__(self):
        return self.data

    def __repr__(self):
        return object.__repr__(self)
