from ..nscoding import NSCoding


class NSMutableData(NSCoding):
    data: bytes

    def __init__(self, data: bytes):
        self.data = data

    @classmethod
    def decode_archive(cls, dearchiver) -> "NSCoding":
        data: bytes = dearchiver.decode("NS.data")
        return cls(data)

    def encode_archive(self, archiver) -> None:
        pass
