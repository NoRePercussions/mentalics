from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from mentalics.nscoding import NSCoding


@dataclass
class NSDate(NSCoding):
    dt: datetime  # unfortunately immutable

    def __init_from_archive__(self, decoder):
        seconds_since_2001_started = Decimal(decoder.decode("NS.time"))
        seconds_since_epoch = seconds_since_2001_started + 978_307_200
        self.__init__(datetime.fromtimestamp(seconds_since_epoch))

    def encode_archive(self, coder) -> None:
        pass
