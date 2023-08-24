import json
import pathlib

from core.object import Object

class Patch(Object):
    def __init__(self, filename=None):
        super().__init__()
        self.name = 'Untitled'
        self.objects: list[Object] = []
        if filename is not None: self.load(filename)

    def add_object(self, obj: Object):
        self.objects.append(obj)

    def load(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.name = data['name']

        self.objects = []
        for obj in data['objects']:
            module = __import__('objects')
            class_ = getattr(module, obj['class'])
            self.objects.append(class_())
            self.objects[-1].set_properties(obj['properties'])

        inds = {obj['id']: i for i, obj in enumerate(data['objects'])}
        for obj, info in zip(self.objects, data['objects']):
            for port, wires in enumerate(info['outputs']):
                for wire in wires:
                    obj.wire(port, self.objects[inds[wire['id']]], wire['port'])

    def serialize(self):
        return {
            'id': self.id,
            'class': self.__class__.__name__,
            'name': self.name,
            'outputs': [[{
                'id': w.object.id,
                'port': w.port
            } for w in io.wires] for io in self.outputs],
            'objects': [obj.serialize() for obj in self.objects],
            'properties': self.properties
        }

    def save(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.serialize(), f, indent=4)


if __name__ == "__main__":
    from objects import *
    p = Patch()
    n1 = Number({'value': 1})
    n2 = Number({'value': 2})
    a = Add()
    pr = Print()
    n1.wire(0, a, 0)
    n2.wire(0, a, 1)
    a.wire(0, pr, 0)
    p.add_object(n1)
    p.add_object(n2)
    p.add_object(a)
    p.add_object(pr)
    p.objects[1].bang()
    p.objects[0].bang()
    p.save('examples/add.json')
    p.load('examples/add.json')
    print(p)
    p.objects[1].bang()
    p.objects[0].bang()
    