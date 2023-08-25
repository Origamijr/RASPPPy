import eel
import os
import numpy as np

from core.runtime import Runtime

eel.init('client', allowed_extensions=['.js', '.html'])

@eel.expose
def pick_file(filename):
    if os.path.exists(filename):
        p = Runtime.open_patch(filename)
        return p.serialize()
    else:
        return np.array([0,1]).tolist()
    
@eel.expose
def toggle_dsp(value):
    if value:
        Runtime.start_dsp()
    else:
        Runtime.stop_dsp()

def close_callback(route, websockets):
    Runtime.stop_dsp()
    os._exit(0)

eel.start('index.html', mode='electron', close_callback=close_callback)