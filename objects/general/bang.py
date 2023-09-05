
from core.object import Object, IOType

class Bang(Object):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.BANG)
        self.add_output(IOType.BANG)

    def bang(self, port=0):
        self.send()