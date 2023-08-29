from core.object import Object, IOType

class Multiply(Object):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.MESSAGE)
        self.add_input(IOType.MESSAGE)
        self.add_output(IOType.MESSAGE)
        
        if len(self.properties['args']) >= 1:
            value = self.properties['args'][0]
            try:
                value = int(value)
            except ValueError:
                value = float(value)
            self.properties['value'] = value
        self.properties = {'value': 1} | self.properties
        
        self.inputs[0].value = 1
        self.inputs[1].value = self.properties['value']

    def bang(self, port=0):
        if port == 0:
            self.outputs[0].value = self.inputs[0].value * self.inputs[1].value
            self.send()