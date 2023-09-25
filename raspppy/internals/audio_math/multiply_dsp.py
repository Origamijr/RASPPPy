import numpy as np
from numbers import Number

from raspppy.core.object import RASPPPyObject, IOType, object_alias
from raspppy.core.audio_server import BUFSIZE

@object_alias('*~')
class Multiply_DSP(RASPPPyObject):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.SIGNAL)
        self.add_input(IOType.ANYTHING)
        self.add_output(IOType.SIGNAL)
        
    def _convert_input_to_signal(self, port):
        if isinstance(self.inputs[port].value, Number):
            self.inputs[port].value = np.full(BUFSIZE, self.inputs[port].value)
        elif not isinstance(self.inputs[port].value, np.ndarray):
            self.inputs[port].value = np.full(BUFSIZE, 1)

    def on_property_change(self, *args, **kwargs):
        if len(args) >= 1:
            self.inputs[1].value = args[0]
            self._convert_input_to_signal(1)

    def bang(self, port=0):
        if 0 <= port <= 1:
            self._convert_input_to_signal(port)

    def process_signal(self):
        self.outputs[0].value = self.inputs[0].value * self.inputs[1].value