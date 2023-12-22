import typing as t
from dataclasses import dataclass

from mentalics.nscoding import NSCoding


@dataclass
class NSAttributedString(NSCoding):
    value: str
    attributes: t.Optional[dict[str, t.Any]]

    def __init_from_archive__(self, decoder) -> "NSCoding":
        value: str = decoder.decode("NSString")

        if "NSAttributes" in decoder._current_container:
            attributes = decoder.decode("NSAttributes")
        else:
            attributes = None

        return self.__init__(value, attributes)

    def encode_archive(self, coder) -> None:
        pass
