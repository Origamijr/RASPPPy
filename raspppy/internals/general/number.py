from numbers import Number

from raspppy.core.object import RASPPPyObject, IOType

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
        self.add_input(IOType.MESSAGE, default=0)
        self.add_output(IOType.MESSAGE)
        self.properties = {'initial_value': 0} | self.properties

        self.value = self.properties['initial_value']
        
    def on_property_change(self, *args, **kwargs):
        if len(args) >= 1:
            value = args[0]
            try:
                value = int(value)
            except ValueError:
                value = float(value)
            self.properties['initial_value'] = value
            self.value = self.properties['initial_value']
        if 'initial_value' in kwargs:
            value = kwargs['initial_value']
            try:
                value = int(value)
            except ValueError:
                value = float(value)
            self.value = self.properties['initial_value']

    def bang(self, port=0):
        if port == 0:
            if isinstance(self.inputs[0], Number):
                self.value = self.inputs[0]
        self.outputs[0].value = self.value
        self.send()