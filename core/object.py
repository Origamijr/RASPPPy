import itertools
import numpy as np
from enum import Enum, auto
from dataclasses import dataclass

from core.config import config
from core.audio_server import BUFSIZE
from core.utils import infer_string_type

class IOType(Enum):
    BANG = 0
    MESSAGE = auto()
    SIGNAL = auto()
    ANYTHING = auto()
    
class WireException(Exception):
    def __init__(self, obj: 'Object', output, msg='', *args, **kwargs):
        super().__init__(f'Invalid output {output} for object {obj.__class__.__name__} id {obj.id}: {msg}', *args, **kwargs)

class PropertyException(Exception):
    def __init__(self, obj: 'Object', property, msg='', *args, **kwargs):
        super().__init__(f'Object {obj.id} of type {obj.__class__.__name__} invalid property {property}: {msg}', *args, **kwargs)

class Object:
    id_iter = itertools.count(start = 1)

    class ObjectIO:
        """
        Represents a single input/output port for an object
        """
        @dataclass
        class WireInfo: 
            object: 'Object'
            port: int
        def __init__(self, type: IOType):
            self.type: IOType = type
            self.wires: list[Object.ObjectIO.WireInfo] = []
            self.value = None

    def __init__(self, *args, **kwargs):
        self.id = next(Object.id_iter)
        self.inputs: list[Object.ObjectIO] = []
        self.outputs: list[Object.ObjectIO]  = []
        
        # Read arguments into the object properties
        self.properties = kwargs if kwargs != ... else dict()
        if 'position' not in self.properties: self.properties['position'] = (0,0)
        if 'args' not in self.properties: self.properties['args'] = list(args)
        if 'text' not in self.properties:
            self.properties['text'] = f"{self.__class__.__name__.lower().replace('_dsp', '~')} {' '.join([str(a) for a in self.properties['args']])}"

        # Additional tags
        self.dsp = False
        self.audio_input = False
        self.audio_output = False


    def serialize(self):
        """
        Return a json serializable representation of the object for saving and gui loading
        """
        return {
            'id': self.id,
            'class': self.__class__.__name__,
            'inputs': [{
                'wires': [{
                    'id': w.object.id,
                    'port': w.port
                } for w in io.wires],
                'type': io.type.name,
            } for io in self.inputs],
            'outputs': [{
                'wires': [{
                    'id': w.object.id,
                    'port': w.port
                } for w in io.wires],
                'type': io.type.name,
            } for io in self.outputs],
            'properties': self.properties
        }
    
    def __repr__(self):
        return repr(self.serialize())
    
    def set_properties(self, *args, **kwargs):
        """ 
        Overwrites the properties with the input arguments. Does not require properties to exist
        """
        self.properties |= kwargs
        if len(args) > 0:
            self.properties['args'] = list(args)

    def change_properties(self, *args, **kwargs):
        """ 
        Overwrites the properties with the input arguments. Requires the properties to exist
        """
        for key in kwargs:
            if key not in self.properties: raise PropertyException(self, key, 'Attempt to change nonexistant property')
        for key in kwargs:
            self.properties[key] = kwargs[key]
        if len(args) > 0:
            self.properties['args'] = list(args)

    def set_position(self, x, y):
        """ 
        Sets the position of the object in the GUI
        """
        self.set_properties(position=(x,y))

    def set_text(self, text):
        """ 
        Sets the display text that is shown in the GUI. Also parses the arges if applicable
        """
        args = [infer_string_type(a) for a in text.split(' ')[1:]]
        self.set_properties(*args, text=text)

    def add_input(self, type: IOType, default=None):
        self.inputs.append(Object.ObjectIO(type))
        if default: self.inputs[-1].value = default
        self._check_signal_port()

    def add_output(self, type: IOType):
        assert type != IOType.ANYTHING, 'Output type must be specific'
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
                   or any([(IOType.SIGNAL in input.type if isinstance(input.type, list) else input.type == IOType.SIGNAL) for input in self.inputs]) \
                   or any([(output.type == IOType.SIGNAL) for output in self.outputs])

    def wire(self, output, other: 'Object', other_input):
        """
        Connects output of this object to the input of another
        """
        if output >= len(self.outputs) or other_input >= len(other.inputs):
            raise WireException(self, output, 'port out of range')
        
        type1 = self.outputs[output].type
        type2 = other.inputs[other_input].type
        if type1 != IOType.BANG and type2 != IOType.ANYTHING and type1 != type2:
            raise WireException(self, output, f'incompatible data types {type1} and {type2}')
        
        self.outputs[output].wires.append(Object.ObjectIO.WireInfo(other, other_input))
        other.inputs[other_input].wires.append(Object.ObjectIO.WireInfo(self, output))
    
    def disconnect(self, out_port, id, in_port):
        """
        Disconnects output of this object from the input of another if a connection exists
        """
        other = [wire for wire in self.outputs[out_port].wires if wire.object.id == id and wire.port == in_port]
        if len(other) == 0: raise WireException(self, out_port, 'disconnecting nonexistant wire')
        other = other[0]
        other.inputs[self.outputs[out_port].port].wires = [wire for wire in other.inputs[in_port].wires if wire.object.id != self.id or wire.port != out_port]
        self.outputs[out_port].wires = [wire for wire in self.outputs[out_port].wires if wire.object.id != id or wire.port != in_port]

    def set_input(self, input, value):
        """
        Sets the value stored in an input port
        """
        self.inputs[input].value = value

    def send(self):
        for output in reversed(self.outputs):
            if output.type == IOType.SIGNAL: continue
            for wire in output.wires:
                if output.type != IOType.BANG and wire.object.inputs[wire.port].type != IOType.BANG:
                    wire.object.set_input(wire.port, output.value)
                wire.object._bang(wire.port)

    def _bang(self, port=0):
        self.bang(port=port)

    def bang(self, port=0):
        raise NotImplementedError(f'{self.__class__.__name__}')

    def process_signal(self):
        raise NotImplementedError(f'DSP object {self.__class__.__name__} process_signal not implemented')

    def _process_signal(self):
        assert self.dsp
        self.process_signal()
        for output in self.outputs:
            if output.type != IOType.SIGNAL: continue
            for wire in output.wires:
                if wire.object.inputs[wire.port].value is not None:
                    wire.object.inputs[wire.port].value += output.value
                else:
                    wire.object.inputs[wire.port].value = output.value

    def reset_dsp(self):
        # Reset DSP object inputs if receiving a signal input
        assert self.dsp
        for input in self.inputs:
            if input.type != IOType.SIGNAL and input.type != IOType.ANYTHING: continue
            for wire in input.wires:
                if wire.object.outputs[wire.port].type == IOType.SIGNAL:
                    input.value = None
                    break


class AudioIOObject(Object):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_io_buffer: np.ndarray = np.zeros(config(['audio', 'chunk_size']))

    def process_signal(self):
        assert self.audio_input or self.audio_output, 'AudioIOObject not designated as audio IO'
        super().process_signal()


import gevent
class AsyncObject(Object):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_output(self, type: IOType):
        assert type != IOType.SIGNAL, "Async blocks cannot output a signal"
        super().add_output(type)

    def _bang(self, port=0):
        gevent.spawn(self.bang, port=port)

    def _process_signal(self):
        gevent.spawn(self.process_signal)

class Blank(Object):
    """
    Simple object that propogates the input to the output
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.ANYTHING)
        self.add_output(IOType.ANYTHING)

    def bang(self, port=0):
        super().bang(port)
        self.outputs[0].value = self.inputs[0].value
        self.send()

class Blank_DSP(Object):
    """
    Simple object that propogates the input to the output
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_input(IOType.SIGNAL)
        self.add_output(IOType.SIGNAL)

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