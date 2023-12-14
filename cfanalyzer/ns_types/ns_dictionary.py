from ..nscoding import NSCoding


class NSDictionary(NSCoding):
    data: dict

    def __init__(self, data: dict):
        self.data = data

    def decode_archive(self, dearchiver) -> "NSCoding":
        keys: list = dearchiver.decode("NS.keys")
        values: list = dearchiver.decode("NS.objects")
        return self.__init__(dict(zip(keys, values)))

    def encode_archive(self, archiver) -> None:
        pass
