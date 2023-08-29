import numpy as np
from numbers import Number

from core.object import Object, IOType
from core.audio_server import SAMPLE_RATE, BUFSIZE

class Multiply_DSP(Object):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.SIGNAL)
        self.add_input(IOType.ANYTHING)
        self.add_output(IOType.SIGNAL)
        
        if len(self.properties['args']) >= 1:
            value = self.properties['args'][0]
            try:
                value = int(value)
            except ValueError:
                value = float(value)
            self.properties['value'] = value
        self.properties = {'value': 1} | self.properties
        self.set_properties(**self.properties)
        
    def convert_input_to_signal(self):
        if isinstance(self.inputs[1].value, Number):
            self.inputs[1].value = np.full(BUFSIZE, self.inputs[1].value)
    
    def set_properties(self, **kwargs):
        if 'value' in kwargs:
            self.inputs[1].value = kwargs['value']
            self.convert_input_to_signal()
        super().set_properties(**kwargs)

    def bang(self, port=0):
        super().bang(port)
        if port == 1:
            self.convert_input_to_signal()

    def process_signal(self):
        self.outputs[0].value = np.multiply(self.inputs[0].value, self.inputs[1].value)