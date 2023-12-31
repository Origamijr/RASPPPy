import numpy as np

from raspppy.core.object import AudioIOObject, IOType

class DAC_DSP(AudioIOObject):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_output = True
        self.properties = {'channels': [0,1]} | self.properties
        self.properties = {'safety': True} | self.properties

        self.channels = []

    def on_property_change(self, *args, **kwargs):
        if 'channels' in kwargs:
            num_channels = len(kwargs['channels'])
            if num_channels > len(self.channels):
                for _ in range(num_channels - len(self.channels)):
                    self.add_input(IOType.SIGNAL)
            else:
                for _ in range(len(self.channels) - num_channels):
                    self.remove_input()
            self.channels = list(kwargs['channels'])

    def process_signal(self):
        self.audio_io_buffer = np.zeros((self.audio_io_buffer.shape[0], max(self.channels)+1))
        if self.properties['safety']: self.audio_io_buffer = np.clip(self.audio_io_buffer, -1., 1.)
        for i, channel in enumerate(self.channels):
            self.audio_io_buffer[:,channel] = self.inputs[i].value