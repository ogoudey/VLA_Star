from .morphology import Morphology
from .morphologies.ava_gen1 import AvaGen1
from .morphologies.so101 import SO101

def combine(a: AvaGen1, b: SO101):
    return Morphology()