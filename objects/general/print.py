from core.object import Object, DataType
from core.logger import log

class Print(Object):
    """
    """

    def __init__(self, state=...):
        super().__init__(state)
        self.add_input(DataType.ANYTHING)

    def bang(self, port=0):
        super().bang(port)
        log(self.inputs[0].value)