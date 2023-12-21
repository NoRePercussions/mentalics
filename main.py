from mentalics import Unarchiver
from other_types import Ignore

test_file = "test.plist"




with open(test_file, "rb") as f:
    unarchiver = Unarchiver(f, error_on_ignored_attributes=False)

    unarchiver.set_class(Ignore, "NSValue")
    unarchiver.set_class(Ignore, "KeyCommand")
    unarchiver.set_class(Ignore, "F53VideoSurface")
    unarchiver.set_class(Ignore, "F53EffectBus")
    unarchiver.set_class(Ignore, "AudioLevelMatrix")

root = unarchiver.decode()

print(root)
