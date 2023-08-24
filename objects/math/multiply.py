from core.object import Object, DataType

class Multiply(Object):
    """
    """

    def __init__(self, state=...):
        super().__init__(state)
        self.add_input(DataType.NUMBER)
        self.add_input(DataType.NUMBER)
        self.add_output(DataType.NUMBER)
        self.state = {'value': 1} | self.state
        self.inputs[1].value = self.state['value']

    def bang(self, port=0):
        super().bang(port)
        if port == 0:
            self.outputs[0].value = self.inputs[0].value * self.inputs[1].value
            self.send()