import numpy as np
from numbers import Number

from raspppy.core.object import RASPPPyObject, IOType, object_alias
from raspppy.core.config import config

@object_alias('*~')
class Multiply_DSP(RASPPPyObject):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.SIGNAL)
        self.add_input(IOType.ANYTHING)
        self.add_output(IOType.SIGNAL)
        
    def on_property_change(self, *args, **kwargs):
        if len(args) >= 1:
            self.inputs[1].value = args[0]

    def process_signal(self):
        self.outputs[0].value = self.inputs[0].value * self.inputs[1].value