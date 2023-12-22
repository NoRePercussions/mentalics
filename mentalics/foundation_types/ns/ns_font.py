from dataclasses import dataclass

from mentalics.nscoding import NSCoding


@dataclass
class NSFont(NSCoding):
    flags: int
    NSName: str
    NSSize: int

    def __init_from_archive__(self, decoder) -> "NSCoding":
        flags: int = decoder.decode("NSfFlags")
        name: str = decoder.decode("NSName")
        size: str = decoder.decode("NSSize")
        return self.__init__(flags, name, size)

    def encode_archive(self, coder) -> None:
        pass
