
from raspppy.core.object import RASPPPyObject, IOType, object_alias

@object_alias('b')
class Bang(RASPPPyObject):
    """
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.BANG)
        self.add_output(IOType.BANG)

    def bang(self, port=0):
        self.send()