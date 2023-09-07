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
        args = self.properties['args']
        if len(args) == 0: args = ['a', 'a']
        for tag in args:
            keys = [key for key, aliases in Trigger.TRIGGER_OUTPUTS.items() if tag in aliases]
            if len(keys) != 1: raise RuntimeException(f'invalid trigger type: {tag}')
            self.output_types.append(keys[0])
            self.add_output(IOType.BANG if keys[0] == 'BANG' else IOType.MESSAGE)
        print(self.outputs)

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