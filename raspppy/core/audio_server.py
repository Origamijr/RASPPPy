import time
import threading
import numpy as np
import sounddevice as sd

from raspppy.core.utils import MovingAverage
from raspppy.core.config import config

class AudioServer:
    sr = config('audio', 'sample_rate')
    bufsize = config('audio', 'chunk_size')
    callbacks = []
    active = False

    last_frame_time = None
    last_frame_duration = None
    frame_duration = MovingAverage(alpha=0.1)
    frame_duration_stability = MovingAverage(alpha=0.1)

    @staticmethod
    def get_default_devices():
        default_input_device, default_output_device = sd.default.device
        default_host_api = None

        # Get host api index from config
        if 'host_api' in config('audio'):
            host_apis = [i for i, a in enumerate(sd.query_hostapis()) if a['name'] == config('audio', 'host_api')]
            if len(host_apis) > 0: default_host_api = host_apis[0]
            else: print(f"Host API [{config('audio', 'host_api')}] not found. Using default.")
        
        # Find appropriate audio input device
        if 'input_device' in config('audio'):
            input_devices = [d for d in sd.query_devices() if d['max_input_channels'] and d['name'] == config('audio', 'input_device')]
            if len(input_devices) > 0:
                default_input_device = input_devices[0]['index']
                input_devices = [d for d in input_devices if default_host_api is None or d['hostapi'] == default_host_api]
                if len(input_devices) > 0: default_input_device = input_devices[0]['index']
                else: print(f"Audio Input [{config('audio', 'input_device')}] for Host API [{config('audio', 'host_api')}] not found. Using default Host API.")
            else: print(f"Audio Input [{config('audio', 'input_device')}] not found. Using default.")
        
        # Find appropriate audio output device
        if 'output_device' in config('audio'):
            output_devices = [d for d in sd.query_devices() if d['max_output_channels'] and d['name'] == config('audio', 'output_device')]
            if len(output_devices) > 0:
                default_output_device = output_devices[0]['index']
                output_devices = [d for d in output_devices if default_host_api is None or d['hostapi'] == default_host_api]
                if len(output_devices) > 0: default_output_device = output_devices[0]['index']
                else: print(f"Audio Output [{config('audio', 'output_device')}] for Host API [{config('audio', 'host_api')}] not found. Using default Host API.")
            else: print(f"Audio Output [{config('audio', 'output_device')}] not found. Using default.")

        return default_input_device, default_output_device

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
                           latency=config('audio','latency') if 'latency' in config('audio') else sd.default.latency)
        print(sum(stream.latency))
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
    print(AudioServer.get_default_devices())
    AudioServer.open()
    AudioServer.add_callback(lambda x: x)
    time.sleep(5)
    AudioServer.close()