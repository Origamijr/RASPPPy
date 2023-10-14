import eel
import os

from raspppy.core.runtime import Runtime
from raspppy.core.object import PropertyException
import raspppy.core.config as conf
from raspppy.core.runtime_data import ALIASES, DISPLAY_CLASSES

@eel.expose
def get_aliases():
    return ALIASES

@eel.expose
def config(*args):
    return conf.config(*args)

@eel.expose
def get_display_scripts():
    return DISPLAY_CLASSES

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