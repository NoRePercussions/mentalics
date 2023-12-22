from dataclasses import dataclass

from ..nscoding import NSCoding
import typing as t


@dataclass
class NSImage(NSCoding):
    accessibility_description: str
    color: t.Any  # eventually: another class
    image_flags: int
    reps: t.Any  # eventually: another class
    resizing_mode: int  # eventually: enum

    def __init_from_archive__(self, decoder) -> "NSCoding":
        accessibility_description = decoder.decode("NSAccessibilityDescription")
        color = decoder.decode("NSColor")
        image_flags = decoder.decode("NSImageFlags")
        reps = decoder.decode("NSReps")
        resizing_mode = decoder.decode("NSResizingMode")
        return self.__init__(
            accessibility_description,
            color,
            image_flags,
            reps,
            resizing_mode,
            )

    def encode_archive(self, coder) -> None:
        pass
