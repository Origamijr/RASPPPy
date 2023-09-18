import itertools
import numpy as np
from enum import Enum, auto
from dataclasses import dataclass

from core.config import config
from core.utils import infer_string_type

# Just some extra "hacks" to add static aliases to subclasses of the object

class ObjectMetaAliasable(type):
    def __new__(cls, name, bases, dct):
        if "_aliases" in dct:
            dct["_aliases"] = [name.lower().replace('_dsp', '~')] + dct["_aliases"]
        else:
            dct["_aliases"] = [name.lower().replace('_dsp', '~')]

        original_init = dct.get("__init__")

        # Call on_property_change after init of lowest subclass
        def new_init(self, *args, **kwargs):
            if original_init:
                original_init(self, *args, **kwargs)
            if original_init.__qualname__.split('.')[0] == self.__class__.__name__:
                self.on_property_change(*self.properties['args'], **self.properties)

        dct["__init__"] = new_init

        return super().__new__(cls, name, bases, dct)

def object_alias(*aliases):
    assert all([isinstance(alias, str) for alias in aliases])
    def decorator(cls):
        if "_aliases" in cls.__dict__:
            cls._aliases += list(aliases)
        else:
            cls._aliases = list(aliases)
        return cls
    return decorator

# Some extra definitions

class IOType(Enum):
    BANG = 0
    MESSAGE = auto()
    SIGNAL = auto()
    ANYTHING = auto()
    
class WireException(Exception):
    def __init__(self, obj: 'RASPPPyObject', output, msg='', *args, **kwargs):
        super().__init__(f'Invalid output {output} for object {obj.__class__.__name__} id {obj.id}: {msg}', *args, **kwargs)

class PropertyException(Exception):
    def __init__(self, obj: 'RASPPPyObject', property, msg='', *args, **kwargs):
        super().__init__(f'Object {obj.id} of type {obj.__class__.__name__} invalid property {property}: {msg}', *args, **kwargs)

class RuntimeException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

# Main code here

class RASPPPyObject(metaclass=ObjectMetaAliasable):
    """
    Base Object class for data manipulation
    """
    id_iter = itertools.count(start = 1)
    _aliases = []

    class ObjectIO:
        """
        Represents a single input/output port for an object
        """
        @dataclass
        class WireInfo: 
            object: 'RASPPPyObject'
            port: int
        def __init__(self, type: IOType):
            self.type: IOType = type
            self.wires: list[RASPPPyObject.ObjectIO.WireInfo] = []
            self.value = None
        def __repr__(self) -> str:
            return f"{self.type}: {self.value}, {self.wires}"

    def __init__(self, *args, **kwargs):
        self.id = next(RASPPPyObject.id_iter)
        self.inputs: list[RASPPPyObject.ObjectIO] = []
        self.outputs: list[RASPPPyObject.ObjectIO]  = []
        
        # Read arguments into the object properties
        self.properties = kwargs if kwargs != ... else dict()
        if 'position' not in self.properties: self.properties['position'] = (0,0)
        if 'args' not in self.properties: self.properties['args'] = list(args)
        if 'text' not in self.properties:
            self.properties['text'] = f"{self.__class__._aliases[0]} {' '.join([str(a) for a in self.properties['args']])}".strip()

        # Additional tags
        self.dsp = False
        self.audio_input = False
        self.audio_output = False
        self.ready = True


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
    
    def on_property_change(self, *args, **kwargs):
        pass

    def set_properties(self, *args, **kwargs):
        """ 
        Overwrites the properties with the input arguments. Does not require properties to exist
        """
        self.properties |= kwargs
        if len(args) > 0:
            self.properties['args'] = list(args)
        self.on_property_change(*args, **kwargs)

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
        self.on_property_change(*args, **kwargs)

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

    def add_input(self, type: IOType=IOType.MESSAGE, default=None):
        self.inputs.append(RASPPPyObject.ObjectIO(type))
        if default is not None: self.inputs[-1].value = default
        self._check_signal_port()

    def add_output(self, type: IOType=IOType.MESSAGE):
        assert type != IOType.ANYTHING, 'Output type must be specific'
        self.outputs.append(RASPPPyObject.ObjectIO(type))
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

    def wire(self, output, other: 'RASPPPyObject', other_input):
        """
        Connects output of this object to the input of another
        """
        if output >= len(self.outputs) or other_input >= len(other.inputs):
            raise WireException(self, output, 'port out of range')
        
        type1 = self.outputs[output].type
        type2 = other.inputs[other_input].type
        if type1 != IOType.BANG and type2 != IOType.ANYTHING and type1 != type2:
            raise WireException(self, output, f'incompatible data types {type1} and {type2}')
        
        self.outputs[output].wires.append(RASPPPyObject.ObjectIO.WireInfo(other, other_input))
        other.inputs[other_input].wires.append(RASPPPyObject.ObjectIO.WireInfo(self, output))
    
    def disconnect(self, out_port, other: 'RASPPPyObject', in_port):
        """
        Disconnects output of this object from the input of another if a connection exists
        """

        other.inputs[in_port].wires = [wire for wire in other.inputs[in_port].wires if wire.object.id != self.id or wire.port != out_port]
        self.outputs[out_port].wires = [wire for wire in self.outputs[out_port].wires if wire.object.id != other.id or wire.port != in_port]

    
    def disconnect_all(self):
        """
        Disconnects all wires connected to the object
        """
        modified = set()
        for io in self.inputs:
            for wire in io.wires:
                wire.object.outputs[wire.port].wires = [wire for wire in wire.object.outputs[wire.port].wires if wire.object.id != self.id]
                modified.add(wire.object.id)
            io.wires = []
        for io in self.outputs:
            for wire in io.wires:
                wire.object.inputs[wire.port].wires = [wire for wire in wire.object.inputs[wire.port].wires if wire.object.id != self.id]
                modified.add(wire.object.id)
            io.wires = []
        return list(modified)


    def set_input(self, port, value):
        """
        Sets the value stored in an input port
        """
        self.inputs[port].value = value

    def send(self, port=None):
        for i, output in reversed(list(enumerate(self.outputs))):
            if port is not None and i != port: continue
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


class AudioIOObject(RASPPPyObject):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.audio_io_buffer: np.ndarray = np.zeros(config('audio', 'chunk_size'))

    def process_signal(self):
        assert self.audio_input or self.audio_output, 'AudioIOObject not designated as audio IO'
        super().process_signal()


import time
from threading import Thread
class AsyncObject(RASPPPyObject):
    """
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_output(self, type: IOType=IOType.MESSAGE):
        assert type != IOType.SIGNAL, "Async blocks cannot output a signal"
        super().add_output(type)

    def _spawn(self, f, *args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs)
        t.start()
        return t

    def _sleep(self, *args, **kwargs):
        return time.sleep(*args, **kwargs)

    def _bang(self, port=0):
        self._spawn(self.bang, port=port)

    def _process_signal(self):
        assert self.dsp
        self._spawn(self.process_signal)

class Blank(RASPPPyObject):
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

class Blank_DSP(RASPPPyObject):
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
    o = RASPPPyObject()
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