# Runtime data that is also accessable by lower level patches and objects

import glob
import importlib.util
import os
import types
import inspect

from raspppy.core.config import config
from raspppy.core.logger import log

MODULE = None
ALIASES = {}
DISPLAY_CLASSES = {}

def import_dir(directory, verbose=False, module=None, display_classes=None):
    from raspppy.core.object import RASPPPyObject
    # With ChatGPT's help, idk what's happening completely here
    module = module if module else types.ModuleType("my_module")
    if not os.path.exists(directory):
        log(f'Warning: library path {directory} not found')
        return module
    for file in glob.glob(f"{directory}/**/*.py", recursive=True):

        # Extract the module name from the file path
        dir_name, file_name = os.path.split(file)
        module_name = os.path.splitext(file_name)[0]

        # Import the module dynamically
        spec = importlib.util.spec_from_file_location(module_name, file)
        module_file = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module_file)

        # Iterate over the attributes of the module
        for attribute_name in dir(module_file):
            # Get the attribute from the module
            attribute = getattr(module_file, attribute_name)
            
            # Check if the attribute is a class
            if inspect.isclass(attribute) \
                    and attribute.__module__ == module_file.__name__ \
                    and issubclass(attribute, RASPPPyObject):
                if attribute_name in dir(module):
                    log(f'WARNING: Duplicate object class {attribute_name} ignored')
                    continue

                # Add the class to the new module
                setattr(module, attribute_name, attribute)
                if verbose: print(attribute_name)

                # Check if there is a corresponding .js file
                if display_classes is None: continue
                js_file = os.path.join(dir_name, f"{module_name}.js")
                if os.path.exists(js_file):
                    with open(js_file, 'r') as f:
                        js_content = f.read()
                    display_class = getattr(attribute, '_display_class', None)
                    if display_class is None: continue
                    display_classes[attribute_name] = {
                        'display_class': display_class,
                        'script': js_content
                    }
    return module

def load_modules(verbose=False):
    global MODULE, ALIASES, DISPLAY_CLASSES
    # Import modules 
    MODULE = import_dir(config('files', 'base_library'), display_classes=DISPLAY_CLASSES, verbose=verbose)
    for external_dir in config('files', 'external_libraries'):
        MODULE = import_dir(external_dir, module=MODULE, display_classes=DISPLAY_CLASSES, verbose=verbose)

    ALIASES = {}
    for name, obj in vars(MODULE).items():
        if isinstance(obj, type):
            for alias_name in obj._aliases:
                if alias_name not in ALIASES:
                    ALIASES[alias_name] = []
                ALIASES[alias_name].append(name)

    for alias, objs in ALIASES.items():
        if len(objs) > 1:
            log(f'{alias} aliases multiple objects, using {objs[0]}')
        ALIASES[alias] = objs[0]

load_modules(verbose=False)

if __name__ == "__main__":
    for name, obj in vars(MODULE).items():
        if isinstance(obj, type):
            print(f"{name}: {obj._aliases} {'display_enabled' if name in DISPLAY_CLASSES else ''}")