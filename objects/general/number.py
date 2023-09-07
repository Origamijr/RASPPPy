from numbers import Number

from core.object import RASPPPyObject, IOType

class Number(RASPPPyObject):
    """
    Stores a number

    Inputs:
        0. Sets the stored number to the input

    Outputs:
        0. Outputs the stored number

    Raises:
        ValueError: Input argument is not a valid number
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.MESSAGE)
        self.add_output(IOType.MESSAGE)
        
        if len(self.properties['args']) >= 1:
            value = self.properties['args'][0]
            try:
                value = int(value)
            except ValueError:
                value = float(value)
            self.properties['value'] = value
        self.properties = {'value': 0} | self.properties

    def bang(self, port=0):
        if port == 0:
            if isinstance(self.inputs[0], Number):
                self.properties['value'] = self.inputs[0]
        self.outputs[0].value = self.properties['value']
        self.send()