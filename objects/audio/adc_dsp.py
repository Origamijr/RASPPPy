import numpy as np

from core.object import AudioIOObject, DataType

class ADC_DSP(AudioIOObject):
    """
    """

    def __init__(self, state=...):
        super().__init__(state)
        self.add_output(DataType.SIGNAL, DataType.SIGNAL)
        self.add_output(DataType.SIGNAL, DataType.SIGNAL)
        self.audio_input = True
        self.state = {'channels': [0,1]} | self.state

    def process_signal(self):
        super().process_signal()
        for i, channel in enumerate(self.state['channels']):
            if channel >= self.audio_io_buffer.shape[1]:
                self.outputs[i].value = np.zeros(self.audio_io_buffer.shape[0])
            else:
                self.outputs[i].value = self.audio_io_buffer[:,channel].copy()