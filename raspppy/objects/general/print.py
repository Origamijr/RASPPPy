from core.object import RASPPPyObject, IOType, object_alias
from core.logger import log

@object_alias('p')
class Print(RASPPPyObject):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.MESSAGE)

    def bang(self, port=0):
        log(self.inputs[0].value)