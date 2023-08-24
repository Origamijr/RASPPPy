import numpy as np

from core.object import AudioIOObject, DataType

class DAC_DSP(AudioIOObject):
    """
    """

    def __init__(self, properties=...):
        super().__init__(properties)
        self.channels = []
        self.audio_output = True
        self.properties = {'channels': [0,1]} | self.properties
        self.set_properties(self.properties)

    def set_properties(self, properties):
        if 'channels' in properties:
            num_channels = len(properties['channels'])
            if num_channels > len(self.channels):
                for _ in range(num_channels - len(self.channels)):
                    self.add_input(DataType.SIGNAL)
            else:
                for _ in range(len(self.channels) - num_channels):
                    self.remove_input()
            self.channels = list(properties['channels'])
        super().set_properties(properties)

    def process_signal(self):
        self.audio_io_buffer = np.zeros((self.audio_io_buffer.shape[0], max(self.channels)+1))
        for i, channel in enumerate(self.channels):
            self.audio_io_buffer[:,channel] = self.inputs[i].value
        super().process_signal()