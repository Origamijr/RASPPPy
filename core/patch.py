import json
from collections import OrderedDict

from core.object import Object, WireException
from core.utils import import_dir
from core.config import config
from core.logger import log
CONFIG = config(['files'])

class Patch(Object):
    def __init__(self, filename=None):
        super().__init__()
        self.name = 'Untitled'
        self.objects: OrderedDict[int, Object] = OrderedDict()
        if filename is not None: self.load(filename)

    def add_object(self, obj: Object):
        self.objects[obj.id] = obj
        return obj

    def get_object(self, id):
        return self.objects[id] if id in self.objects else None

    def load(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.name = data['name']

        self.objects = {}
        id_map = dict()
        module = import_dir(CONFIG['base_library'])
        for info in data['objects']:
            class_ = getattr(module, info['class'])
            obj = class_()
            id_map[info['id']] = obj.id
            self.objects[obj.id] = obj
            self.objects[obj.id].set_properties(**info['properties'])

        for obj, info in zip(self.objects.values(), data['objects']):
            for port, io in enumerate(info['outputs']):
                for wire in io['wires']:
                    obj.wire(port, self.objects[id_map[wire['id']]], wire['port'])

    def serialize(self):
        return {
            'id': self.id,
            'class': self.__class__.__name__,
            'name': self.name,
            'outputs': [[{
                'id': w.object.id,
                'port': w.port
            } for w in io.wires] for io in self.outputs],
            'objects': [obj.serialize() for obj in self.objects.values()],
            'properties': self.properties
        }

    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.serialize(), f, indent=2)

    def wire(self, src_id, src_port, dest_id, dest_port):
        self.objects[src_id].wire(src_port, self.objects[dest_id], dest_port)
        
    def disconnect(self, src_id, src_port, dest_id, dest_port):
        self.objects[src_id].disconnect(src_port, self.objects[dest_id], dest_port)
        
    def change_properties(self, id, *args, **kwargs):
        self.objects[id].change_properties(*args, **kwargs)
        


if __name__ == "__main__":
    import gevent
    module = import_dir('objects')
    globals().update({name: module.__dict__[name] for name in module.__dict__ if not name.startswith('_')})
    
    p = Patch()
    
    b  = p.add_object(Bang(position=(0,0)))
    t  = p.add_object(Trigger('b', 'b', position=(0,50)))
    n1 = p.add_object(Number(1, position=(0,100)))
    n2 = p.add_object(Number(2, position=(100,100)))
    a  = p.add_object(Add(position=(0,150)))
    pr = p.add_object(Print(position=(0,200)))
    
    b.wire(0, t, 0)
    t.wire(0, n1, 0)
    t.wire(1, n2, 0)
    n1.wire(0, a, 0)
    n2.wire(0, a, 1)
    a.wire(0, pr, 0)

    list(p.objects.values())[0].bang()
    
    p.save('examples/add_example.json')
    p.load('examples/add_example.json')
    print(p)
    list(p.objects.values())[0].bang()
    