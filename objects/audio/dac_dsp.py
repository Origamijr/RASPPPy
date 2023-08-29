import numpy as np

from core.object import AudioIOObject, IOType

class DAC_DSP(AudioIOObject):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channels = []
        self.audio_output = True
        self.properties = {'channels': [0,1]} | self.properties
        self.set_properties(**self.properties)

    def set_properties(self, **kwargs):
        if 'channels' in kwargs:
            num_channels = len(kwargs['channels'])
            if num_channels > len(self.channels):
                for _ in range(num_channels - len(self.channels)):
                    self.add_input(IOType.SIGNAL)
            else:
                for _ in range(len(self.channels) - num_channels):
                    self.remove_input()
            self.channels = list(kwargs['channels'])
        super().set_properties(**kwargs)

    def process_signal(self):
        self.audio_io_buffer = np.zeros((self.audio_io_buffer.shape[0], max(self.channels)+1))
        for i, channel in enumerate(self.channels):
            self.audio_io_buffer[:,channel] = self.inputs[i].value