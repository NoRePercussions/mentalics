import typing as t
import plistlib as pl

if t.TYPE_CHECKING:
    from .dearchiver import Decoder


class NSCoding:
    """
    Indicates that a class can be encoded/decoded
    by Archiver/Dearchiver
    """

    @classmethod
    def decode_archive(self, dearchiver: t.Any) -> "NSCoding": ...

    def encode_archive(self, archiver: t.Any) -> None: ...

    def __getattribute__(self, item):
        """Return values when settings are accessed"""
        val = super().__getattribute__(item)
        if isinstance(val, UnresolvedNSCoding):
            return val.get_original_object()
        else:
            return val



class UnresolvedNSCoding:
    """
    Represents an object that has been deserialized
    in an attribute of another object. When it is seen
    while accessing an NSCoding object's attributes,
    it can be resolved back to the original attribute
    by the NSCoding method.
    """

    decoder: "Decoder"
    uid: pl.UID

    def __init__(self, decoder: "Decoder", uid: pl.UID):
        self.decoder = decoder
        self.uid = uid

    def get_original_object(self) -> NSCoding:
        return self.dearchiver.get_object(self.uid)
