from mentalics import Dearchiver
from other_types import Ignore

test_file = "test.plist"

dearchiver = Dearchiver()

dearchiver.set_class(Ignore, "NSValue")

dearchiver.set_class(Ignore, "KeyCommand")
dearchiver.set_class(Ignore, "F53VideoSurface")
dearchiver.set_class(Ignore, "F53EffectBus")
dearchiver.set_class(Ignore, "AudioLevelMatrix")

with open(test_file, "rb") as f:
    root = dearchiver.load(f)

print(root)
