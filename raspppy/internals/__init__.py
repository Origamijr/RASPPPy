"""
from pathlib import Path

# Include all classes when 'from mypkg import *' is called. 
fs = [f for f in Path('objects').rglob('*.py') if not f.name.startswith('_')]

for f in [str(f).replace('/', '.').replace('\\', '.')[:-3] for f in fs]:
    statement = f'from {f} import *'
    exec(statement)
"""