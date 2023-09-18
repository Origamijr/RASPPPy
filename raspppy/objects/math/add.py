from core.object import RASPPPyObject, object_alias

@object_alias('+')
class Add(RASPPPyObject):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(default=0)
        self.add_input(default=0)
        self.add_output()
        self.properties = {'value': 0} | self.properties

    def on_property_change(self, *args, **kwargs):
        if len(args) >= 1:
            value = args[0]
            try:
                value = int(value)
            except ValueError:
                value = float(value)
            self.properties['value'] = value
            self.inputs[1].value = self.properties['value']

    def bang(self, port=0):
        if port == 0:
            self.outputs[0].value = self.inputs[0].value + self.inputs[1].value
            self.send()