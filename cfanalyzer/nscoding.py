import typing as t


class NSCoding:
    """
    Indicates that a class can be encoded/decoded
    by Archiver/Dearchiver
    """

    def decode_archive(self, dearchiver: t.Any) -> "NSCoding": ...

    def encode_archive(self, archiver: t.Any) -> None: ...
