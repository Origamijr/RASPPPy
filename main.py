import eel
import os
import glob

from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
import warnings

warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)

from core.runtime import Runtime
from core.config import config as conf

eel.init('client', allowed_extensions=['.js', '.html'])

@eel.expose
def get_aliases():
    from core.runtime_data import ALIASES
    return ALIASES

@eel.expose
def config(*args):
    return conf(*args)

@eel.expose
def get_js_scripts(directory):
    js_scripts = {}
    for file in glob.glob(f"{directory}/**/*.js", recursive=True):
        with open(file, 'r') as f:
            script_content = f.read()
            class_name = os.path.splitext(os.path.basename(file))[0].lower()
            js_scripts[class_name] = script_content
    return js_scripts

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