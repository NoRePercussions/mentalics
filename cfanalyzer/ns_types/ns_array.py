from ..nscoding import NSCoding


class NSArray(NSCoding, list):
    def decode_archive(self, dearchiver) -> "NSCoding":
        data = dearchiver.decode("NS.objects")
        return self.__init__(data)

    def encode_archive(self, archiver) -> None:
        pass
