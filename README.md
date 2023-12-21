# Mentalics

> [!WARNING]  
> This library is not stable yet.

`mentalics` is designed primarily to read, write, and analyze NSKeyedArchiver-generated archives as Python object graphs. It is designed to reflect the `NSCoder` interface, handle circular references, and efficiently work through unknown classes and files.

## Usage

Exploring an unknown archive (not stable):

```python3
from mentalics import Explorer

with open("my.plist", "rb") as file:
    explorer = Explorer(file)

print(explorer._classes)
```

Decoding a known archive:

```python3
from mentalics import Unarchiver, NSCoding
from dataclasses import dataclass


@dataclass
class MyClass(NSCoding):
    my_attr: str

    def __init_from_archive__(self, decoder) -> "NSCoding":
        my_attr = decoder.decode("myAttr")
        return self.__init__(my_attr)

    def encode_archive(self, encoder) -> None:
        encoder.encode(self.my_attr, for_key="myAttr")


with open("my.plist", "rb") as file:
    dearchiver = Unarchiver(file)
    dearchiver.set_class(MyClass, "MyClass")
    
root = dearchiver.decode()
print(root)
```

## Why `mentalics`?

There are many other libraries for parsing plists and archives: [plistlib](https://docs.python.org/3/library/plistlib.html) and [bplist-python](https://github.com/farcaller/bplist-python) (plists, not archives), [bpylist](https://github.com/Marketcircle/bpylist) and [bpylist2](https://github.com/parabolala/bpylist2), [plistutils](https://github.com/strozfriedberg/plistutils), [ccl-bplist](https://github.com/cclgroupltd/ccl-bplist), and probably others.

However, there is mismatched support for desirable features:

- Handling circular references (ccl-bplist)
- NSCoder/NSCoding-like interface (bpylist, bpylist2)
- Simple handling of NSValues (none)
- Exploring archives with unknown structure (ccl-bplist)
- Generating code for classes from archives (none)

All of these are either a part of `mentalics` or a planned feature.
