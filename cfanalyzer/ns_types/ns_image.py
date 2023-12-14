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

    @classmethod
    def decode_archive(cls, dearchiver) -> "NSCoding":
        accessibility_description = dearchiver.decode("NSAccessibilityDescription")
        color = dearchiver.decode("NSColor")
        image_flags = dearchiver.decode("NSImageFlags")
        reps = dearchiver.decode("NSReps")
        resizing_mode = dearchiver.decode("NSResizingMode")
        return cls(
            accessibility_description,
            color,
            image_flags,
            reps,
            resizing_mode,
            )

    def encode_archive(self, archiver) -> None:
        pass
