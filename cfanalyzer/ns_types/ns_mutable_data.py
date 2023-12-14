from ..nscoding import NSCoding


class NSMutableData(NSCoding):
    data: bytes

    def __init__(self, data: bytes):
        self.data = data

    def decode_archive(self, dearchiver) -> "NSCoding":
        data: bytes = dearchiver.decode("NS.data")
        return self.__init__(data)

    def encode_archive(self, archiver) -> None:
        pass
