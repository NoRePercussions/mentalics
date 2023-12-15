from ..nscoding import NSCoding


class NSDictionary(NSCoding, dict):
    def __init_from_archive__(self, decoder) -> "NSCoding":
        keys: list = decoder.decode("NS.keys")
        values: list = decoder.decode("NS.objects")
        return self.__init__(zip(keys, values))

    def encode_archive(self, coder) -> None:
        pass
