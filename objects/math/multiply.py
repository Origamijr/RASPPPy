from core.object import Object, DataType

class Multiply(Object):
    """
    """

    def __init__(self, properties=...):
        super().__init__(properties)
        self.add_input(DataType.NUMBER)
        self.add_input(DataType.NUMBER)
        self.add_output(DataType.NUMBER)
        self.properties = {'value': 1} | self.properties
        self.inputs[1].value = self.properties['value']

    def bang(self, port=0):
        super().bang(port)
        if port == 0:
            self.outputs[0].value = self.inputs[0].value * self.inputs[1].value
            self.send()