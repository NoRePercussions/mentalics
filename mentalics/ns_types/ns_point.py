from dataclasses import dataclass

from ..nscoding import NSCoding


@dataclass
class NSPoint(NSCoding):
    x: int
    y: int

    def __init_from_archive__(self, decoder) -> "NSCoding":
        # NSPoint is stored as an NSValue with NS.pointval -> "{x, y}"
        as_string: str = decoder.decode("NS.pointval")

        values_as_strings: list[str] = as_string.lstrip("{").rstrip("}").split(", ")
        values = [int(x) for x in values_as_strings]

        assert len(values) == 2
        x, y = values
        return self.__init__(x, y)

    def encode_archive(self, coder) -> None:
        pass
