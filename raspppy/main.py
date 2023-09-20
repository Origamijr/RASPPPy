import eel
import os
import glob

from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
import warnings

warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)

from core.runtime import Runtime
from core.object import PropertyException
from core.config import config as conf

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

@eel.expose
def update_object_properties(patch_id, object_id, properties):
    modified = set()
    obj = Runtime.patches[patch_id].objects[object_id]
    [modified.add(wire.object.id) for io in obj.inputs for wire in io.wires]
    [modified.add(wire.object.id) for io in obj.outputs for wire in io.wires]
    try:
        args = properties['args'] if 'args' in properties else []
        kwargs = {k: v for k, v in properties.items() if k != 'args'}
        obj.change_properties(*args, **kwargs)
        modified.add(obj.id)
    except PropertyException:
        return []
    return [Runtime.patches[patch_id].objects[id].serialize() for id in modified]

@eel.expose
def remove_objects(patch_id, objs):
    removed = set()
    modified = set()
    for obj_id in objs:
        modified.update(Runtime.patches[patch_id].remove_object(obj_id))
        removed.add(obj_id)
    modified = modified - removed
    return list(removed), [Runtime.patches[patch_id].objects[id].serialize() for id in modified]


@eel.expose
def bang_object(patch_id, object_id, port):
    Runtime.patches[patch_id].bang_object(object_id, port)

@eel.expose
def wire(patch_id, wires, connect):
    modified = set()
    for wire in wires:
        if Runtime.patches[patch_id].wire(wire['src_id'], wire['src_port'], wire['dest_id'], wire['dest_port'], connect=connect):
            modified.add(wire['src_id'])
            modified.add(wire['dest_id'])
    return [Runtime.patches[patch_id].objects[id].serialize() for id in modified]

def start_client():
    import sys
    print(sys.argv)

    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'node_modules')):
        import subprocess
        # Check npm is installed
        try:
            subprocess.run(['npm', '--version'], shell=True, check=True, stdout=subprocess.PIPE)
        except FileNotFoundError:
            print('npm is not installed. Please install npm to use this application.')
            exit(1)

        # Install dependencies (should just be electron and its dependencies)
        try:
            subprocess.run(['npm', 'install'], shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f'Error: {e}')
            exit(1)

    eel.init('client', allowed_extensions=['.js', '.html'])
    
    def close_callback(route, websockets):
        Runtime.stop_dsp()
        os._exit(0)
    
    eel.start('index.html', mode='electron', close_callback=close_callback, blocking=False)

if __name__ == "__main__":
    start_client()