import numpy as np

from core.patch import Patch
from core.object import Blank, Blank_DSP, DataType, AudioIOObject
from core.audio_server import AudioServer
from core.logger import log
from core.config import config
CONFIG = config(['audio'])

class Runtime():
    patches: Patch = []
    arrays = dict()
    dsp_order = []
    dsp = False

    @staticmethod
    def new_patch():
        Runtime.patches.append(Patch())
        return Runtime.patches[-1]

    @staticmethod
    def open_patch(filename) -> Patch:
        Runtime.patches.append(Patch(filename))
        return Runtime.patches[-1]
    
    @staticmethod
    def save_patch(filename):
        Runtime.patches[0].save(filename) # TODO hard coded

    @staticmethod
    def compute_dsp_graph() -> Patch:
        Runtime.dsp_order = []
        objects = [object for patch in Runtime.patches for object in patch.objects if object.dsp]
        # TODO also add the eventual blank objects created for inlets/outlets/send/rec~
        
        seen = set()
        def topological_sort_helper(dsp_node):
            for output in dsp_node.outputs:
                if output.type != DataType.SIGNAL or (isinstance(output.type, list) and DataType.SIGNAL not in output.type): continue
                for wire in output.wires:
                    if wire.object not in seen:
                        seen.add(wire.object)
                        topological_sort_helper(wire.object)
            Runtime.dsp_order.insert(0, dsp_node)

        for object in objects:
            if object not in seen:
                topological_sort_helper(object)
        
        cycle = False
        seen = set()
        for object in Runtime.dsp_order:
            for output in object.outputs:
                if output.type != DataType.SIGNAL or (isinstance(output.type, list) and DataType.SIGNAL not in output.type): continue
                for wire in output.wires:
                    if wire.object in seen:
                        cycle = True
                        Runtime.dsp_order = []
                        break
            seen.add(object)
        
        return not cycle
    
    @staticmethod
    def compute_dsp(in_data: np.ndarray):
        # Reset connected inputs to zero
        for object in Runtime.dsp_order:
            object.reset_dsp()
        
        # Set inputs
        for object in Runtime.dsp_order:
            if isinstance(object, AudioIOObject) and object.audio_input:
                object.audio_io_buffer = in_data.copy()

        # Run Computation
        for object in Runtime.dsp_order:
            object._process_signal()
            #if len(object.outputs) > 0: print(object.__class__.__name__, object.outputs[0].value)

        # Collect Outputs
        output = np.zeros((CONFIG['chunk_size'],1))
        for object in Runtime.dsp_order:
            if isinstance(object, AudioIOObject) and object.audio_output:
                if output.size < object.audio_io_buffer.size:
                    temp = object.audio_io_buffer.copy()
                    temp[:,:output.shape[1]] += output
                else:
                    temp = output.copy()
                    temp[:,:object.audio_io_buffer.shape[1]] += object.audio_io_buffer
                output = temp
        
        return output

    @staticmethod
    def start_dsp():
        if not Runtime.compute_dsp_graph(): return
        Runtime.dsp = True
        AudioServer.open()
        AudioServer.add_callback(Runtime.compute_dsp)
        log('DSP Enabled')

    @staticmethod
    def stop_dsp():
        Runtime.dsp = False
        AudioServer.close()
        log('DSP Disabled')

if __name__ == "__main__":
    from objects import *
    import time
    p = Patch()
    adc = ADC_DSP()
    dac = DAC_DSP()
    ph = Phasor_DSP({'freq': 660})
    g = Multiply_DSP({'value': 0.01})
    l = Multiply_DSP({'value': 0.9})
    p.add_object(adc)
    p.add_object(dac)
    p.add_object(ph)
    p.add_object(g)
    p.add_object(l)
    adc.wire(0, l, 0)
    ph.wire(0, g, 0)
    g.wire(0, l, 0)
    l.wire(0, dac, 0)
    l.wire(0, dac, 1)
    p.save('examples/phasor_loopback.json')
    Runtime.open_patch('examples/phasor_loopback.json')
    print(Runtime.compute_dsp_graph())
    Runtime.start_dsp()
    time.sleep(5)
    Runtime.stop_dsp()
