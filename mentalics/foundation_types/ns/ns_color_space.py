from dataclasses import dataclass

from mentalics.nscoding import AutoNSCoding


@dataclass
class NSColorSpace(AutoNSCoding):
    NSICC: bytes
    NSID: int  # Is this an enum to something?
