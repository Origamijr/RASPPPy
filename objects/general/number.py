from core.object import Object, DataType

class Number(Object):
    """
    Stores a number

    Inputs:
        0. Number: Sets the stored number to the input

    Outputs:
        0. Number: Outputs the stored number
    """
    def __init__(self, properties=...):
        super().__init__(properties)
        self.add_input(DataType.NUMBER)
        self.add_output(DataType.NUMBER)
        self.properties = {'value': 0} | self.properties

    def bang(self, port=0):
        super().bang(port)
        self.outputs[0].value = self.properties['value']
        self.send()