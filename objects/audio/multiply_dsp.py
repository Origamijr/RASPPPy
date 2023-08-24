import numpy as np
from numbers import Number

from core.object import Object, DataType
from core.audio_server import SAMPLE_RATE, BUFSIZE

class Multiply(Object):
    """
    """

    def __init__(self, state=...):
        super().__init__(state)
        self.add_input(DataType.SIGNAL)
        self.add_input([DataType.NUMBER, DataType.SIGNAL])
        self.add_output(DataType.NUMBER)
        self.state = {'value': 1} | self.state
        self.inputs[1].value = self.state['value']
        
    def convert_input_to_signal(self):
        if isinstance(self.inputs[1].value, Number):
            self.inputs[1].value = np.full(BUFSIZE, self.inputs[1].value)

    def bang(self, port=0):
        super().bang(port)
        if port == 1:
            self.convert_input_to_signal()

    def process_signal(self):
        super().process_signal()
        self.outputs[0].value = np.multiply(self.inputs[0].value, self.inputs[1].value)