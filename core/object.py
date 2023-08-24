import itertools
import numpy as np
from enum import Enum, auto
from dataclasses import dataclass

from core.config import config
from core.audio_server import BUFSIZE

class DataType(Enum):
    BANG = 0
    NUMBER = auto()
    STRING = auto()
    SIGNAL = auto()
    ARRAY = auto()
    LIST = auto()
    DICTIONARY = auto()
    ANYTHING = auto()

    def default(cls):
        match cls:
            case DataType.BANG: return None
            case DataType.NUMBER: return 0
            case DataType.SIGNAL: return None
            case DataType.ARRAY: return np.array([])
            case DataType.STRING: return ''
            case DataType.LIST: return []
            case DataType.DICTIONARY: return dict()
            case DataType.ANYTHING: return None
    
class WireException(Exception):
    def __init__(self, obj: 'Object', output, msg='', *args, **kwargs):
        super().__init__(f'Invalid output {output} for object {obj.__class__.__name__} id {obj.id}: {msg}', *args, **kwargs)

class Object:
    id_iter = itertools.count(start = 1)

    class ObjectIO:
        @dataclass
        class WireInfo: 
            object: 'Object'
            port: int
        def __init__(self, type: DataType|list[DataType]):
            assert isinstance(type, DataType) or (DataType.BANG not in type and DataType.ANYTHING not in type), 'Invalid IO port type'
            self.type: DataType|list[DataType] = type
            self.wires: list[Object.ObjectIO.WireInfo] = []
            self.value = type[0].default() if isinstance(type, list) else type.default()

    def __init__(self, properties=...):
        self.id = next(Object.id_iter)
        self.inputs: list[Object.ObjectIO] = []
        self.outputs: list[Object.ObjectIO]  = []
        self.properties = properties if properties != ... else dict()
        self.dsp = False
        self.audio_input = False
        self.audio_output = False

    def serialize(self):
        return {
            'id': self.id,
            'class': self.__class__.__name__,
            'outputs': [[{
                'id': w.object.id,
                'port': w.port
            } for w in io.wires] for io in self.outputs],
            'properties': self.properties
        }
    
    def __repr__(self):
        return repr(self.serialize())
    
    def set_properties(self, properties):
        self.properties |= properties

    def add_input(self, type: DataType|list[DataType]):
        self.inputs.append(Object.ObjectIO(type))
        self._check_signal_port()

    def add_output(self, type: DataType|list[DataType]):
        assert not (isinstance(type, list) and len(type) > 1 and DataType.SIGNAL in type), 'SIGNAL type output must be only'
        self.outputs.append(Object.ObjectIO(type))
        self._check_signal_port()

    def remove_input(self):
        assert len(self.inputs > 0)
        wires = self.inputs[-1].wires
        for wire in wires:
            wire.object.disconnect(wire.port, wire.object.id)
        self.inputs.pop()
        self._check_signal_port()

    def remove_output(self):
        assert len(self.outputs > 0)
        wires = self.outputs[-1].wires
        for wire in wires:
            self.disconnect(len(self.outputs) - 1, wire.object.id)
        self.outputs.pop()
        self._check_signal_port()

    def _check_signal_port(self):
        self.dsp = self.audio_input or self.audio_output \
                   or any([(DataType.SIGNAL in input.type if isinstance(input.type, list) else input.type == DataType.SIGNAL) for input in self.inputs]) \
                   or any([(DataType.SIGNAL in output.type if isinstance(output.type, list) else output.type == DataType.SIGNAL) for output in self.outputs])

    def wire(self, output, other: 'Object', other_input):
        if output >= len(self.outputs) or other_input >= len(other.inputs):
            raise WireException(self, output, 'port out of range')
        
        type1 = self.outputs[output].type
        type2 = other.inputs[other_input].type
        type1 = type1 if isinstance(type1, list) else [type1]
        type2 = type2 if isinstance(type2, list) else [type2]
        # Bangs should be compatible with all types, otherwise outputs must be subset of inputs
        if not (type1[0] == DataType.BANG or type2[0] == DataType.BANG) and (type2[0] != DataType.ANYTHING and not set(type1).issubset(set(type2))):
            raise WireException(self, output, 'incompatible data types')
        
        self.outputs[output].wires.append(Object.ObjectIO.WireInfo(other, other_input))
        other.inputs[other_input].wires.append(Object.ObjectIO.WireInfo(self, output))
    
    def disconnect(self, port, id):
        other = [o for o in self.outputs[port].wires if o.object.id == id][0]
        other.inputs[self.outputs[port].port].wires = [wire for wire in other.inputs[self.outputs[port].port].wires if wire.object.id != self.id]
        self.outputs[port].wires = [wire for wire in self.outputs[port].wires if wire.object.id != id]

    def set(self, input, value):
        self.inputs[input].value = value

    def send(self):
        for output in reversed(self.outputs):
            if output.type == DataType.SIGNAL: continue
            for wire in output.wires:
                if output.type != DataType.BANG and wire.object.inputs[wire.port].type != DataType.BANG:
                    wire.object.set(wire.port, output.value)
                wire.object.bang(wire.port)

    def bang(self, port=0):
        assert 0 <= port < len(self.inputs)

    def process_signal(self):
        assert self.dsp
        for output in self.outputs:
            if output.type != DataType.SIGNAL: continue
            for wire in output.wires:
                wire.object.inputs[wire.port].value += output.value

    def reset_dsp(self):
        assert self.dsp
        for input in self.inputs:
            if input.type != DataType.SIGNAL or (isinstance(input.type, list) and DataType.SIGNAL not in input.type): continue
            for wire in input.wires:
                if wire.object.outputs[wire.port].type == DataType.SIGNAL:
                    input.value = np.zeros(BUFSIZE)
                    break


class AudioIOObject(Object):
    """
    """

    def __init__(self, properties=...):
        super().__init__(properties)
        self.audio_io_buffer: np.ndarray = np.zeros(config(['audio', 'chunk_size']))

    def process_signal(self):
        assert self.audio_input or self.audio_output, 'AudioIOObject not designated as audio IO'
        super().process_signal()

class Blank(Object):
    """
    Simple object that propogates the input to the output
    """
    def __init__(self, properties=...):
        super().__init__(properties)
        self.add_input(DataType.ANYTHING)
        self.add_output(DataType.ANYTHING)

    def bang(self, port=0):
        super().bang(port)
        self.outputs[0].value = self.inputs[0].value
        self.send()

class Blank_DSP(Object):
    """
    Simple object that propogates the input to the output
    """
    def __init__(self, properties=...):
        super().__init__(properties)
        self.add_input(DataType.SIGNAL)
        self.add_output(DataType.SIGNAL)

    def process_signal(self):
        super().process_signal()
        self.outputs[0].value = self.inputs[0].value


if __name__ == "__main__":
    o = Object()
    o.set_properties({'a': 1})
    print(o)
    o.set_properties({'a': 2})
    print(o)
    o.set_properties({'b': 3})
    print(o)
    o.set_properties({'b': 4, 'c':5})
    print(o)
    o.set_properties({'a': 6, 'b': 7, 'c':8})
    print(1 in [[1], 2])