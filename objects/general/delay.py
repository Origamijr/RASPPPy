import gevent

from core.object import AsyncObject, IOType

class Delay(AsyncObject):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.MESSAGE)
        self.add_input(IOType.MESSAGE, default=0)
        self.add_output(IOType.MESSAGE)

        if len(self.properties['args']) >= 1:
            self.inputs[1].value = float(self.properties['args'][0])

    def bang(self, port=0):
        if port == 0:
            data = self.inputs[0].value
            gevent.sleep(self.inputs[1].value / 1000)
            self.outputs[0].value = data
            self.send()