import numpy as np
from numbers import Number

from raspppy.core.object import RASPPPyObject, IOType
from raspppy.core.config import config
CONFIG = config('audio')

class Phasor_DSP(RASPPPyObject):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.ANYTHING)
        self.add_output(IOType.SIGNAL)
        
        self.last_value = 0

    def _convert_input_to_signal(self):
        # Convert port 0 input to a constant signal if it's a number
        if isinstance(self.inputs[0].value, Number):
            self.inputs[0].value = np.full(CONFIG['chunk_size'], self.inputs[0].value)
        elif not isinstance(self.inputs[0].value, np.ndarray):
            self.inputs[0].value = np.full(CONFIG['chunk_size'], 0)

    def on_property_change(self, *args, **kwargs):
        if len(args) >= 1:
            self.inputs[0].value = args[0]
            self._convert_input_to_signal()

    def bang(self, port=0):
        if port == 0:
            self._convert_input_to_signal()

    def process_signal(self):
        # Convert frequency to rate
        deltas = self.inputs[0].value / CONFIG['sample_rate']

        # The rate is just the first derivative, so a cumulative sum would give a ramp at constant rate
        # add the last value to set initial value
        deltas[0] += self.last_value

        # Cumulative sum
        self.outputs[0].value = np.mod(np.cumsum(deltas), 1)
        
        # Store last value
        self.last_value = self.outputs[0].value[-1]

