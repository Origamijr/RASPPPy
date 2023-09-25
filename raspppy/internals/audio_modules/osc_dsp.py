import numpy as np
from numbers import Number

from raspppy.core.object import RASPPPyObject, IOType
from raspppy.core.config import config

class Osc_DSP(RASPPPyObject):
    """
    Untested
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.ANYTHING)
        self.add_output(IOType.SIGNAL)

        self.chunk_size = config('audio', 'chunk_size')
        self.sr = config('audio', 'sample_rate')
        
        self.last_value = 1.+0.j

    def _convert_input_to_signal(self):
        # Convert port 0 input to a constant signal if it's a number
        if isinstance(self.inputs[0].value, Number):
            self.inputs[0].value = np.full(self.chunk_size, self.inputs[0].value)
        elif not isinstance(self.inputs[0].value, np.ndarray):
            self.inputs[0].value = np.full(self.chunk_size, 0)

    def on_property_change(self, *args, **kwargs):
        if len(args) >= 1:
            self.inputs[0].value = args[0]
            self._convert_input_to_signal()

    def bang(self, port=0):
        if port == 0:
            self._convert_input_to_signal()

    def process_signal(self):
        # If we want to allow variable frequency, we'll probably need to use complex multiplication
        # P.S., I made a 5$ bet with my friend that this was faster than the normal wavetable approach (in python with numpy). I won.

        # convert frequency to a cumulative angle (imaginary) around the unit circle
        angle = np.cumsum(self.inputs[0].value / self.sr) * 2 * np.pi

        # Complex multiply the current position on the unit circle by the imaginary angle
        # Performance of using complex numbers seems to depend on array size with boundary ~512
        if self.chunk_size > 512:
            # Approach using only real numbers to perform complex multiplication
            rate_r = np.cos(angle)
            rate_i = np.sin(angle)
            # The output is the real part of the complex multiplication
            sig = rate_r * self.last_value.real + rate_i * self.last_value.imag
            # Update last value, clipping to correct numerical errors
            self.last_value = np.clip(sig[-1], -1, 1) + np.clip(rate_r[-1] * self.last_value.imag - rate_i[-1] * self.last_value.real, -1, 1) * 1j
        else:
            # Approach using just straight up complex multiplication
            angle = self.last_value * np.exp(1j * angle)
            # The output is just the real part
            sig = np.real(angle)
            # Update the last value, clipping it to the unit circle for numerical stability
            self.last_value = sig[-1]/np.abs(sig[-1]).max()

        self.outputs[0].value = sig

