import numpy as np
from numbers import Number

from core.object import Object, DataType
from core.audio_server import SAMPLE_RATE, BUFSIZE
from core.runtime import Runtime

class Phasor_DSP(Object):
    """
    """

    def __init__(self, properties=...):
        super().__init__(properties)
        self.add_input([DataType.SIGNAL, DataType.NUMBER])
        self.add_output(DataType.SIGNAL)
        self.properties = {'freq': 440} | self.properties
        self.set_properties(self.properties)
        self.last_value = 0

    def convert_input_to_signal(self):
        if isinstance(self.inputs[0].value, Number):
            self.inputs[0].value = np.full(BUFSIZE, self.inputs[0].value)

    def set_properties(self, properties):
        if 'freq' in properties:
            self.inputs[0].value = self.properties['freq']
            self.convert_input_to_signal()
        super().set_properties(properties)

    def bang(self, port=0):
        if port == 0:
            self.convert_input_to_signal()
        super().bang(port)

    def process_signal(self):
        deltas = self.inputs[0].value / SAMPLE_RATE
        deltas[0] += self.last_value
        self.outputs[0].value = np.mod(np.cumsum(deltas), 1)
        self.last_value = self.outputs[0].value[-1]
        super().process_signal()

