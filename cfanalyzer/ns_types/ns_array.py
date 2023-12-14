from ..nscoding import NSCoding


class NSArray(NSCoding):
    data: list

    def __init__(self, data):
        self.data = data

    @classmethod
    def decode_archive(cls, dearchiver) -> "NSCoding":
        data = dearchiver.decode("NS.objects")
        return cls(data)

    def encode_archive(self, archiver) -> None:
        pass
