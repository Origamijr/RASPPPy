import numpy as np
from numbers import Number

from core.object import Object, DataType
from core.audio_server import SAMPLE_RATE, BUFSIZE
from core.runtime import Runtime

class Phasor_DSP(Object):
    """
    """

    def __init__(self, state=...):
        super().__init__(state)
        self.add_input([DataType.SIGNAL, DataType.NUMBER])
        self.add_output(DataType.SIGNAL)
        self.state = {'freq': 0} | self.state
        self.inputs[0].value = self.state['freq']
        self.convert_input_to_signal()
        self.last_value = 0

    def convert_input_to_signal(self):
        if isinstance(self.inputs[0].value, Number):
            self.inputs[0].value = np.full(BUFSIZE, self.inputs[0].value)

    def bang(self, port=0):
        super().bang(port)
        if port == 0:
            self.convert_input_to_signal()

    def process_signal(self):
        super().process_signal()
        deltas = self.inputs[0].value / SAMPLE_RATE
        deltas[0] += self.last_value
        self.outputs[0].value = np.mod(np.cumsum(deltas), 1)
        self.last_value = self.outputs[0].value[-1]

