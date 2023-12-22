from dataclasses import dataclass

from mentalics.nscoding import NSCoding


@dataclass
class NSUUID(NSCoding):
    data: bytes

    def __init_from_archive__(self, decoder):
        data = decoder.decode("NS.uuidbytes")
        self.__init__(data)

    def encode_archive(self, coder) -> None:
        pass
