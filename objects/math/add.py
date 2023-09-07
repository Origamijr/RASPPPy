from core.object import RASPPPyObject, IOType

class Add(RASPPPyObject):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.MESSAGE, default=0)
        self.add_input(IOType.MESSAGE, default=0)
        self.add_output(IOType.MESSAGE)
        
        if len(self.properties['args']) >= 1:
            value = self.properties['args'][0]
            try:
                value = int(value)
            except ValueError:
                value = float(value)
            self.properties['value'] = value
        self.properties = {'value': 0} | self.properties

        self.inputs[0].value = 0
        self.inputs[1].value = self.properties['value']

    def bang(self, port=0):
        if port == 0:
            self.outputs[0].value = self.inputs[0].value + self.inputs[1].value
            self.send()