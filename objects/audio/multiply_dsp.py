import numpy as np
from numbers import Number

from core.object import Object, IOType, PropertyException
from core.audio_server import BUFSIZE

class Multiply_DSP(Object):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.SIGNAL)
        self.add_input(IOType.ANYTHING)
        self.add_output(IOType.SIGNAL)
        self.set_properties(**self.properties)
        
    def _convert_input_to_signal(self):
        if isinstance(self.inputs[1].value, Number):
            self.inputs[1].value = np.full(BUFSIZE, self.inputs[1].value)
        elif not isinstance(self.inputs[1].value, np.ndarray):
            self.inputs[1].value = np.full(BUFSIZE, 1)

    def set_properties(self, *args, **kwargs):
        super().set_properties(*args, **kwargs)
        
        if len(self.properties['args']) >= 1:
            self.inputs[1].value = self.properties['args'][0]
        self._convert_input_to_signal()

    def bang(self, port=0):
        if port == 1:
            self._convert_input_to_signal()

    def process_signal(self):
        self.outputs[0].value = np.multiply(self.inputs[0].value, self.inputs[1].value)