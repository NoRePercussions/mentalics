from dataclasses import dataclass

from ..nscoding import NSCoding


@dataclass
class NSData(NSCoding):
    data: bytes

    def decode_archive(self, dearchiver) -> "NSCoding":
        data: bytes = dearchiver.decode("NS.data")
        return self.__init__(data)

    def encode_archive(self, archiver) -> None:
        pass

    def __bytes__(self):
        return self.data

    def __repr__(self):
        return object.__repr__(self)
