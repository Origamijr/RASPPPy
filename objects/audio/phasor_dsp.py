import numpy as np
from numbers import Number

from core.object import Object, IOType
from core.runtime import Runtime
from core.config import config
CONFIG = config(['audio'])


class Phasor_DSP(Object):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.ANYTHING)
        self.add_output(IOType.SIGNAL)

        if len(self.properties['args']) >= 1:
            value = self.properties['args'][0]
            try:
                value = int(value)
            except ValueError:
                value = float(value)
            self.properties['freq'] = value
        
        self.properties = {'freq': 0} | self.properties
        self.set_properties(**self.properties)
        self.last_value = 0

    def _convert_input_to_signal(self):
        # Convert port 0 input to a constant signal if it's a number
        if isinstance(self.inputs[0].value, Number):
            self.inputs[0].value = np.full(CONFIG['chunk_size'], self.inputs[0].value)

    def set_properties(self, **kwargs):
        if 'freq' in kwargs:
            self.inputs[0].value = kwargs['freq']
            self._convert_input_to_signal()
        super().set_properties(**kwargs)

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

