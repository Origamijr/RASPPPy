import numpy as np
from numbers import Number

from core.object import Object, DataType
from core.audio_server import SAMPLE_RATE, BUFSIZE

class Multiply_DSP(Object):
    """
    """

    def __init__(self, properties=...):
        super().__init__(properties)
        self.add_input(DataType.SIGNAL)
        self.add_input([DataType.NUMBER, DataType.SIGNAL])
        self.add_output(DataType.SIGNAL)
        self.properties = {'value': 1} | self.properties
        self.set_properties(self.properties)
        
    def convert_input_to_signal(self):
        if isinstance(self.inputs[1].value, Number):
            self.inputs[1].value = np.full(BUFSIZE, self.inputs[1].value)
    
    def set_properties(self, properties):
        if 'value' in properties:
            self.inputs[1].value = properties['value']
            self.convert_input_to_signal()
        super().set_properties(properties)

    def bang(self, port=0):
        super().bang(port)
        if port == 1:
            self.convert_input_to_signal()

    def process_signal(self):
        self.outputs[0].value = np.multiply(self.inputs[0].value, self.inputs[1].value)