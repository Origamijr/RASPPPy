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
            json.dump(self.serialize(), f, indent=4)

    def wire(self, src_id, src_port, dest_id, dest_port):
        self.objects[src_id].wire(src_port, self.objects[dest_id], dest_port)
        
    def disconnect(self, src_id, src_port, dest_id, dest_port):
        self.objects[src_id].disconnect(src_port, self.objects[dest_id], dest_port)
        
    def change_properties(self, id, *args, **kwargs):
        self.objects[id].change_properties(*args, **kwargs)
        


if __name__ == "__main__":
    module = import_dir('objects')
    globals().update({name: module.__dict__[name] for name in module.__dict__ if not name.startswith('_')})
    p = Patch()
    n1 = Number(1, position=(0,0))
    n2 = Number(2, position=(100,0))
    a = Add(position=(0,50))
    pr = Print(position=(0,100))
    n1.wire(0, a, 0)
    n2.wire(0, a, 1)
    a.wire(0, pr, 0)
    p.add_object(n1)
    p.add_object(n2)
    p.add_object(a)
    p.add_object(pr)
    list(p.objects.values())[1].bang()
    list(p.objects.values())[0].bang()
    p.save('examples/add_example.json')
    p.load('examples/add_example.json')
    print(p)
    list(p.objects.values())[1].bang()
    list(p.objects.values())[0].bang()
    