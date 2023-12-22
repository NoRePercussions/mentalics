from ..nscoding import NSCoding


class NSArray(NSCoding, list):
    def __init_from_archive__(self, decoder) -> "NSCoding":
        data = decoder.decode("NS.objects")
        return self.__init__(data)

    def encode_archive(self, coder) -> None:
        pass
