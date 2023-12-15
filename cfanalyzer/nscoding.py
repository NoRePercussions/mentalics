import typing as t

if t.TYPE_CHECKING:
    from .dearchiver import Decoder


class NSCoding:
    """
    Indicates that a class can be encoded/decoded
    by Archiver/Dearchiver

    Example usage:

    class MyClass(NSCoding):
        def __init_from_archive__(self, dearchiver) -> "NSCoding":
            super().__init_from_archive__(dearchiver)
            self.my_attr = dearchiver.decode("myAttr")
            return self

        def encode_archive(self, archiver) -> None:
            super().encode_archive(archiver)
            archiver.encode("myAttr", self.myAttr)
    """

    def __init_from_archive__(self, decoder: "Decoder") -> "NSCoding":
        return self

    def encode_archive(self, coder) -> None:
        return
