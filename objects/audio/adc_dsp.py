import numpy as np

from core.object import AudioIOObject, IOType

class ADC_DSP(AudioIOObject):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.channels = []
        self.audio_input = True
        self.properties = {'channels': [0,1]} | self.properties
        self.set_properties(**self.properties)

    def set_properties(self, *args, **kwargs):
        if 'channels' in kwargs:
            num_channels = len(kwargs['channels'])
            if num_channels > len(self.channels):
                for _ in range(num_channels - len(self.channels)):
                    self.add_output(IOType.SIGNAL)
            else:
                for _ in range(len(self.channels) - num_channels):
                    self.remove_output()
            self.channels = list(kwargs['channels'])
        super().set_properties(*args, **kwargs)

    def process_signal(self):
        for i, channel in enumerate(self.channels):
            if channel >= self.audio_io_buffer.shape[1]:
                self.outputs[i].value = np.zeros(self.audio_io_buffer.shape[0])
            else:
                self.outputs[i].value = self.audio_io_buffer[:,channel].copy()