import typing as t
from dataclasses import dataclass
from enum import Enum

from mentalics.nscoding import NSCoding


class NSColorSpaceCode(Enum):
    calibrated_rgb = 1  # NSRGB key, sometimes comes with a custom color space
    device_rgb = 2
    calibrated_white = 3  # NSWhite key
    device_white = 4
    device_cmyk = 5  # NSCMYK key


# This class probably needs rewriting by someone more
# familiar with the way it is serialized.

@dataclass
class NSColor(NSCoding):
    color_space: NSColorSpaceCode
    data: bytes  # Could be: custom color space data, or RGBA, CMYK, or White

    custom_color_space: t.Optional["NSColorSpace"]

    def __init_from_archive__(self, decoder) -> "NSCoding":
        color_space: NSColorSpaceCode = NSColorSpaceCode(decoder.decode("NSColorSpace"))
        custom_color_space: t.Optional["NSColorSpace"] = None
        data: bytes

        if color_space == NSColorSpaceCode.calibrated_rgb:
            # Either RGB, or a custom encoding
            if "NSCustomColorSpace" in decoder._current_container:
                # We need to handle a custom color space
                custom_color_space = decoder.decode("NSCustomColorSpace")

            data = decoder.decode("NSRGB")
        elif color_space == NSColorSpaceCode.device_rgb:
            data = decoder.decode("NSRGB")
        elif color_space == NSColorSpaceCode.calibrated_white:
            data = decoder.decode("NSWhite")
        elif color_space == NSColorSpaceCode.device_white:
            data = decoder.decode("NSWhite")
        elif color_space == NSColorSpaceCode.device_cmyk:
            data = decoder.decode("NSCMYK")
        else:
            raise ValueError(f"Unknown color space code {color_space}")

        self.__init__(color_space, data, custom_color_space)

    def encode_archive(self, coder) -> None:
        pass
