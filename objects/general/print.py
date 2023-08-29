from core.object import Object, IOType
from core.logger import log

class Print(Object):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.MESSAGE)

    def bang(self, port=0):
        log(self.inputs[0].value)