import glob
import importlib.util
import inspect
import os
import types
from core.logger import log

def import_dir(directory, verbose=False, module=None):
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
            if inspect.isclass(attribute) and attribute.__module__ == module_file.__name__:
                if attribute_name in dir(module):
                    log(f'WARNING: Duplicate object class {attribute_name} ignored')
                    continue

                # Add the class to the new module
                setattr(module, attribute_name, attribute)
                if verbose: print(attribute_name)
    return module

def filter_kwargs(kwargs, exclude=None, adapt_f=None):
    if adapt_f is not None:
        sig = inspect.signature(adapt_f)
        filter_keys = [param.name for param in sig.parameters.values() if param.kind == param.POSITIONAL_OR_KEYWORD]
        kwargs = {filter_key: kwargs[filter_key] for filter_key in filter_keys if filter_key in kwargs}
    if exclude is not None:
        kwargs = {key: kwargs[key] for key in kwargs if key not in exclude}
    return kwargs

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

class MovingAverage:
    def __init__(self, alpha=0):
        self.alpha = alpha
        self.value = 0
        self.n = 0

    def add(self, x, count=1):
        self.n += count
        if self.alpha == 0:
            self.value += count * (x - self.value) / self.n
        else:
            self.value *= 1 - self.alpha
            self.value += self.alpha * x
        return self.value
    
    def reset(self):
        self.value = 0
        self.n = 0

from functools import wraps
from time import time

def timing(f):
    @wraps(f)
    def wrap(*args, **kw):
        ts = time()
        result = f(*args, **kw)
        te = time()
        print('func:%r args:[%r, %r] took: %2.4f sec' % \
          (f.__name__, args, kw, te-ts))
        return result
    return wrap

def infer_string_type(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s