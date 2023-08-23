import pyaudio
import json

from core.config import config
CONFIG = config(['audio'])

class AudioServer:
    def __init__(self):
        self.sr = CONFIG['sample_rate']
        self.bufsize = CONFIG['chunk_size']
        self.audio = pyaudio.PyAudio()

        self.get_devices()
    
    def get_devices(self):
        self.input_devices = []
        self.output_devices = []
        self.host_apis = [self.audio.get_host_api_info_by_index(i)['name'] for i in range(self.audio.get_host_api_count())]

        devices = [self.audio.get_device_info_by_index(i)['name'] for i in range(self.audio.get_device_count())]
        for device in devices:
            try:
                deviceName = device['name'].encode('shift-jis').decode('utf-8')
            except (UnicodeDecodeError, UnicodeEncodeError):
                deviceName = device['name']

            if device['maxInputChannels'] > 0:
                self.input_devices.append({"index": device['index'], "name": deviceName, "hostApi": device['hostApi']})
            if device['maxOutputChannels'] > 0:
                self.output_devices.append({"index": device['index'], "name": deviceName, "hostApi": device['hostApi']})
        
        assert len(self.input_devices) > 0 and len(self.output_devices) > 0
        self.default_in_device = self.input_devices[0]
        self.default_out_device = self.output_devices[0]


if __name__ == "__main__":
    audio = AudioServer()