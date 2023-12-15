from ..nscoding import NSCoding


class NSDictionary(NSCoding, dict):
    def decode_archive(self, dearchiver) -> "NSCoding":
        keys: list = dearchiver.decode("NS.keys")
        values: list = dearchiver.decode("NS.objects")
        return self.__init__(zip(keys, values))

    def encode_archive(self, archiver) -> None:
        pass
