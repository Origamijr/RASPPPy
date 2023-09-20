import time
import threading
import numpy as np
import sounddevice as sd

from raspppy.core.utils import MovingAverage
from raspppy.core.config import config
CONFIG = config('audio')
SAMPLE_RATE = CONFIG['sample_rate']
BUFSIZE = CONFIG['chunk_size']

class AudioServer:
    sr = SAMPLE_RATE
    bufsize = BUFSIZE
    callbacks = []
    active = False

    last_frame_time = None
    last_frame_duration = None
    frame_duration = MovingAverage(alpha=0.1)
    frame_duration_stability = MovingAverage(alpha=0.1)

    @staticmethod
    def get_default_devices():
        host_apis = [a for a in sd.query_hostapis()]
        input_devices = [d for d in sd.query_devices() if d['max_input_channels']]
        output_devices = [d for d in sd.query_devices() if d['max_output_channels']]
        default_host_api = [i for i, a in enumerate(host_apis) if a['name'] == CONFIG['host_api']][0] \
                            if 'host_api' in CONFIG else 0
        default_input_device = 0
        default_output_device = 0
        #TODO figure out how to tie to config file. sort of low priority
        return tuple(sd.default.device)

    input_device, output_device = get_default_devices()
    
    @staticmethod
    def callback(indata, outdata, frames, timing, status: sd.CallbackFlags):
        start = time.perf_counter()
        if AudioServer.last_frame_time:
            AudioServer.last_frame_duration = timing.currentTime - AudioServer.last_frame_time
            AudioServer.frame_duration.add(AudioServer.last_frame_duration)
            AudioServer.frame_duration_stability.add((AudioServer.frame_duration.value - AudioServer.last_frame_duration) ** 2)
        AudioServer.last_frame_time = timing.currentTime

        # capture the outputs
        out = np.zeros(outdata.shape)
        for fn in AudioServer.callbacks:
            out += fn(indata)[:,:out.shape[1]]
        outdata[:] = out

        # Audio processing load check
        elapsed_time = time.perf_counter() - start
        if AudioServer.frame_duration.value > 0: 
            dsp_load = elapsed_time / AudioServer.frame_duration.value
            if dsp_load > 0.9:
                print(f'WARNING: High DSP load {dsp_load}')

    @staticmethod
    def run_server():
        stream = sd.Stream(callback=AudioServer.callback, 
                           dtype=np.float32,
                           samplerate=AudioServer.sr,
                           blocksize=AudioServer.bufsize,
                           device=(AudioServer.input_device, AudioServer.output_device),
                           channels=sd.default.channels,
                           latency=CONFIG['latency'] if 'latency' in CONFIG else sd.default.latency)
        with stream:
            while AudioServer.active:
                time.sleep(0.1)
    
    @staticmethod
    def open():
        AudioServer.active = True
        thread = threading.Thread(name='audio_server', target=AudioServer.run_server)
        thread.start()

    @staticmethod
    def close():
        AudioServer.active = False
        time.sleep(0.1)
        AudioServer.callbacks = []

    @staticmethod
    def add_callback(fn):
        AudioServer.callbacks.append(fn)


if __name__ == "__main__":
    AudioServer.open()
    time.sleep(5)
    AudioServer.close()