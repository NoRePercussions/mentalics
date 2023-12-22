from dataclasses import dataclass

from mentalics.nscoding import NSCoding


@dataclass
class NSURL(NSCoding):
    base: str
    relative: str

    def __init_from_archive__(self, decoder) -> "NSCoding":
        base: str = decoder.decode("NS.base")
        relative: str = decoder.decode("NS.relative")
        return self.__init__(base, relative)

    def encode_archive(self, coder) -> None:
        pass
