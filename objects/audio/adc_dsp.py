import numpy as np

from core.object import AudioIOObject, DataType

class ADC_DSP(AudioIOObject):
    """
    """

    def __init__(self, properties=...):
        super().__init__(properties)
        self.channels = []
        self.audio_input = True
        self.properties = {'channels': [0,1]} | self.properties
        self.set_properties(self.properties)

    def set_properties(self, properties):
        if 'channels' in properties:
            num_channels = len(properties['channels'])
            if num_channels > len(self.channels):
                for _ in range(num_channels - len(self.channels)):
                    self.add_output(DataType.SIGNAL)
            else:
                for _ in range(len(self.channels) - num_channels):
                    self.remove_output()
            self.channels = list(properties['channels'])
        super().set_properties(properties)

    def process_signal(self):
        for i, channel in enumerate(self.channels):
            if channel >= self.audio_io_buffer.shape[1]:
                self.outputs[i].value = np.zeros(self.audio_io_buffer.shape[0])
            else:
                self.outputs[i].value = self.audio_io_buffer[:,channel].copy()
        super().process_signal()