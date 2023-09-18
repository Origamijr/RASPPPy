# Singleton Runtime object to coordinate patches and DSP

import numpy as np

from core.patch import Patch
from core.object import Blank, Blank_DSP, IOType, AudioIOObject
from core.audio_server import AudioServer
from core.logger import log
from core.config import config

class Runtime():
    module = None
    patches: dict[int,Patch] = dict()
    arrays = dict()
    dsp_order = []
    dsp = False

    @staticmethod
    def new_patch():
        patch = Patch()
        Runtime.patches[patch.id] = patch
        return patch

    @staticmethod
    def open_patch(filename) -> Patch:
        patch = Patch(filename)
        Runtime.patches[patch.id] = patch
        return patch
    
    @staticmethod
    def save_patch(patch_id, filename):
        Runtime.patches[patch_id].save(filename) # TODO hard coded

    @staticmethod
    def compute_dsp_graph() -> Patch:
        Runtime.dsp_order = []

        # flatten all dsp objects in the runtime
        objects = [object for patch in Runtime.patches.values() for object in patch.objects.values() if object.dsp]
        # TODO also add the eventual blank objects created for inlets/outlets/send/rec~
        
        seen = set()
        def topological_sort_helper(dsp_node):
            for output in dsp_node.outputs:
                if output.type != IOType.SIGNAL or (isinstance(output.type, list) and IOType.SIGNAL not in output.type): continue
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
                if output.type != IOType.SIGNAL or (isinstance(output.type, list) and IOType.SIGNAL not in output.type): continue
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

        # Collect Outputs
        output = np.zeros((config('audio', 'chunk_size'),1))
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
    import time
    from core.runtime_data import import_dir
    module = import_dir('objects')
    globals().update({name: module.__dict__[name] for name in module.__dict__ if not name.startswith('_')})
    
    p = Patch()

    adc = p.add_object(ADC_DSP(position=(100,0)))
    ph  = p.add_object(Phasor_DSP(660, position=(200,0)))
    g   = p.add_object(Multiply_DSP(0.01, position=(200,50)))
    vad = p.add_object(VAD_DSP(position=(0,50)))
    whs = p.add_object(Whisper(position=(0,100)))
    l   = p.add_object(Multiply_DSP(0.9, position=(100,100)))
    dac = p.add_object(DAC_DSP(position=(100,150)))
    pr  = p.add_object(Print(position=(0,150)))
    
    adc.wire(0, l, 0)
    adc.wire(0, vad, 0)
    ph.wire(0, g, 0)
    g.wire(0, l, 0)
    l.wire(0, dac, 0)
    l.wire(0, dac, 1)
    vad.wire(1, pr, 0)
    vad.wire(0, whs, 0)
    whs.wire(0, pr, 0)

    p.save('../examples/phasor_loopback.json')
    p = Runtime.open_patch('../examples/phasor_loopback.json')
    print(Runtime.compute_dsp_graph(), Runtime.dsp_order)
    Runtime.start_dsp()
    time.sleep(10)
    Runtime.stop_dsp()
