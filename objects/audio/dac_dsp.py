import numpy as np

from core.object import AudioIOObject, DataType

class ADC_DSP(AudioIOObject):
    """
    """

    def __init__(self, state=...):
        super().__init__(state)
        self.add_input(DataType.SIGNAL, DataType.SIGNAL)
        self.add_input(DataType.SIGNAL, DataType.SIGNAL)
        self.audio_input = True
        self.state = {'channels': [0,1]} | self.state

    def process_signal(self):
        super().process_signal()
        self.audio_io_buffer = np.zeros((self.audio_io_buffer[0], max(self.state['channels'])+1))
        for i, channel in enumerate(self.state['channels']):
            self.audio_io_buffer[:,channel] = self.inputs[i].value