import numpy as np
from numbers import Number

from core.object import RASPPPyObject, IOType, PropertyException
from core.audio_server import BUFSIZE

class Multiply_DSP(RASPPPyObject):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.SIGNAL)
        self.add_input(IOType.ANYTHING)
        self.add_output(IOType.SIGNAL)
        
    def _convert_input_to_signal(self):
        if isinstance(self.inputs[1].value, Number):
            self.inputs[1].value = np.full(BUFSIZE, self.inputs[1].value)
        elif not isinstance(self.inputs[1].value, np.ndarray):
            self.inputs[1].value = np.full(BUFSIZE, 1)

    def on_property_change(self, *args, **kwargs):
        if len(args) >= 1:
            self.inputs[1].value = args[0]
            self._convert_input_to_signal()

    def bang(self, port=0):
        if port == 1:
            self._convert_input_to_signal()

    def process_signal(self):
        self.outputs[0].value = np.multiply(self.inputs[0].value, self.inputs[1].value)