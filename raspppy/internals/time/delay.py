from raspppy.core.object import AsyncObject

class Delay(AsyncObject):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input()
        self.add_input(default=0)
        self.add_output()

    def on_property_change(self, *args, **kwargs):
        if len(args) >= 1:
            self.inputs[1].value = float(args[0])

    def bang(self, port=0):
        if port == 0:
            data = self.inputs[0].value
            self._sleep(self.inputs[1].value / 1000)
            self.outputs[0].value = data
            self.send()