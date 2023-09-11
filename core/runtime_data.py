# Runtime data that is also accessable by lower level patches and objects

import glob
import importlib.util
import os
import types
import inspect

from core.config import config
from core.logger import log

MODULE = None
ALIASES = {}

def import_dir(directory, verbose=False, module=None):
    from core.object import RASPPPyObject
    # From ChatGPT
    module = module if module else types.ModuleType("my_module")
    for file in glob.glob(f"{directory}/**/*.py", recursive=True):
        # Extract the module name from the file path
        module_name = os.path.splitext(os.path.basename(file))[0]

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
    return module

def load_modules(verbose=False):
    global MODULE, ALIASES
    # Import modules 
    MODULE = import_dir(config('files', 'base_library'), verbose=verbose)
    for external_dir in config('files', 'external_libraries'):
        MODULE = import_dir(external_dir, module=MODULE, verbose=verbose)

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