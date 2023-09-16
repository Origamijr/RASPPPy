import numpy as np

from core.object import RASPPPyObject, IOType, RuntimeException

class Trigger(RASPPPyObject):
    """
    """
    TRIGGER_OUTPUTS = {
        'BANG': ['b', 'bang'],
        'INT': ['i', 'int', 'integer'],
        'FLOAT': ['f', 'float'],
        'STRING': ['s', 'string', 'symbol'],
        'LIST': ['l', 'list'],
        'TENSOR': ['t', 'tensor', 'array', 'ndarray'],
        'ANYTHING': ['a', 'any', 'anything'],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.MESSAGE)
        self.output_types = []

    def on_property_change(self, *args, **kwargs):
        if len(args) == 0 and len(self.output_types) == 0: args = ['a', 'a']
        if len(args) > 0:
            # Parse the arguments into types from aliases
            new_types = []
            for tag in args:
                keys = [key for key, aliases in Trigger.TRIGGER_OUTPUTS.items() if tag in aliases]
                if len(keys) != 1: raise RuntimeException(f'invalid trigger type: {tag}')
                new_types.append(keys[0])
            # Remove old outputs if needed
            while len(self.output_types) > len(new_types):
                self.remove_output()
                self.output_types.pop()
            # Iterate over new output types
            for i, new_type in enumerate(new_types):
                if i < len(self.output_types):
                    # Modify existing output type
                    if self.output_types[i] == 'BANG' and new_type != 'BANG':
                        # Disconnect any previously valid bangs to signal inputs if no longer bang
                        to_disconnect = []
                        for wire in self.outputs[i].wires:
                            if wire.object.outputs[wire.port].type == IOType.SIGNAL:
                                to_disconnect.append((wire.object.id, wire.port))
                        for other_id, in_port in to_disconnect:
                            self.disconnect(i, other_id, in_port)
                    self.output_types[i] = new_type
                else:
                    # Append new type if more new types remain
                    self.output_types.append(new_type)
                    self.add_output(IOType.BANG if new_type == 'BANG' else IOType.MESSAGE)

    def bang(self, port=0):
        if port == 0:
            data = self.inputs[0].value
            for io, type in zip(self.outputs, self.output_types):
                match type:
                    case 'INT':
                        try:
                            io.value = int(data)
                        except:
                            io.value = 0
                    case 'FLOAT':
                        try:
                            io.value = float(data)
                        except:
                            io.value = 0.
                    case 'STRING':
                        try:
                            io.value = str(data)
                        except:
                            io.value = 0.
                    case 'LIST':
                        try:
                            io.value = list(data)
                        except:
                            io.value = [data]
                    case 'TENSOR':
                        try:
                            io.value = np.array(list(data))
                        except:
                            try:
                                io.value = np.array([data])
                            except:
                                io.value = np.array([0])
                    case _:
                        io.value = data
            self.send()