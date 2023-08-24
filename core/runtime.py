

from core.patch import Patch
from core.audio_server import AudioServer

class Runtime():
    patches = []
    arrays = dict()
    dsp_order = []

    def compute_dsp_graph():
        pass

    def start_dsp():
        if not Runtime.compute_dsp_graph(): return
        AudioServer.open()
        AudioServer.add_callback()

    def stop_dsp():
        AudioServer.close()
