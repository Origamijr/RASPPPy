import eel
import os
import glob
import sys
import argparse
import subprocess
import shutil

try:
    from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
    import warnings

    warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
    warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)
except:
    pass

from raspppy.core.runtime import Runtime
from raspppy.core.object import PropertyException
import raspppy.core.config as conf
from raspppy.core.runtime_data import MODULE, ALIASES

@eel.expose
def get_aliases():
    return ALIASES

@eel.expose
def config(*args):
    return conf.config(*args)

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
def update_object_properties(patch_id, obj_ids, properties):
    modified = set()
    for obj_id, prop in zip(obj_ids, properties):
        obj = Runtime.patches[patch_id].objects[obj_id]
        [modified.add(wire.object.id) for io in obj.inputs for wire in io.wires]
        [modified.add(wire.object.id) for io in obj.outputs for wire in io.wires]
        try:
            args = prop['args'] if 'args' in prop else []
            kwargs = {k: v for k, v in prop.items() if k != 'args'}
            obj.change_properties(*args, **kwargs)
            modified.add(obj_id)
        except PropertyException:
            return []
    return [Runtime.patches[patch_id].objects[id].serialize() for id in modified]

@eel.expose
def put_objects(patch_id, properties):
    """
    Create objects in patch from its properties. Assumes 'text' is a property
    """
    added = []
    for prop in properties:
        assert 'text' in prop
        added.append(Runtime.patches[patch_id].add_object(prop).serialize())
    return added

@eel.expose
def remove_objects(patch_id, obj_ids):
    removed = set()
    modified = set()
    for obj_id in obj_ids:
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



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?', default=None, help='optional - file to open')
    parser.add_argument('--config', default=os.path.join(os.path.dirname(__file__), 'config.toml'), type=str, help='path to alternative config file')
    parser.add_argument('--electron', default=None, type=str, help='path to electron executable')
    args = parser.parse_args(sys.argv[1:])

    conf.reload(args.config)

    if args.electron:
        # Use electron provided as an argument
        electron_path = os.path.abspath(args.electron)
    else:
        electron_path = shutil.which('electron')
        if electron_path:
            # Use default electron if installed already
            electron_path = os.path.abspath(electron_path)

        else: 
            # Use a locally downloaded electron
            if not os.path.exists(os.path.join(os.path.dirname(__file__), 'node_modules')):
                # Last resort, install electron
                # Check npm is installed
                try:
                    subprocess.run(['npm', '--version'], shell=True, check=True, stdout=subprocess.PIPE)
                except FileNotFoundError:
                    print('npm is not installed. Please install npm to use this application.')
                    exit(1)

                # Install dependencies (should just be electron and its dependencies)
                try:
                    subprocess.run(['npm', 'install'], shell=True, check=True, cwd=os.path.dirname(__file__))
                except subprocess.CalledProcessError as e:
                    print(f'Error: {e}')
                    exit(1)
            electron_path = os.path.join(os.path.dirname(__file__), 'node_modules/electron/dist/electron')

    # change the path so electron sees the correct package.json
    os.chdir(os.path.dirname(__file__))

    # Start the client
    eel.init('client', allowed_extensions=['.js', '.html'])
    eel.browsers.set_path('electron', electron_path)
    
    def close_callback(route, websockets):
        Runtime.stop_dsp()
        os._exit(0)
    
    eel.start('index.html', mode='electron', close_callback=close_callback, blocking=False)

if __name__ == "__main__":
    sys.argv.append('examples/add_example.json')
    main()