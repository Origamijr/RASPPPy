import eel
import os
import numpy as np

from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
import warnings

warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)

from core.runtime import Runtime
from core.config import config as conf

from threading import Thread

eel.init('client', allowed_extensions=['.js', '.html'])

@eel.expose
def config(*args):
    conf(*args)

@eel.expose
def open_patch(filename):
    if os.path.exists(filename):
        p = Runtime.open_patch(filename)
        return p.serialize()
    else:
        return None
    
@eel.expose
def save_patch(filename):
    Runtime.save_patch(filename)
    
@eel.expose
def toggle_dsp(value):
    if value:
        Runtime.start_dsp()
    else:
        Runtime.stop_dsp()

def close_callback(route, websockets):
    Runtime.stop_dsp()
    os._exit(0)

eel.start('index.html', mode='electron', close_callback=close_callback, blocking=False)