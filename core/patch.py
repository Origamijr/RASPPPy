import json
import pathlib

from core.object import Object

class Patch(Object):
    def __init__(self):
        super().__init__()
        self.name = 'Untitled'
        self.objects: list[Object] = []

    def add_object(self, obj: Object):
        self.objects.append(obj)

    def load(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self.name = data['name']

        self.objects = []
        for obj in data:
            module = __import__('objects')
            class_ = getattr(module, obj['class'])
            self.objects.append(class_())

        inds = {obj.id: i for i, obj in enumerate(self.objects)}
        for obj, info in zip(self.objects, data):
            for port, wires in enumerate(info['outputs']):
                for wire in wires:
                    obj.wire(port, self.objects[inds[wire.id]], wire.port)

    def serialize(self):
        return {
            'id': self.id,
            'class': self.__class__.__name__,
            'name': self.name,
            'outputs': [[{
                'id': w.object.id,
                'port': w.port
            } for w in io.wires] for io in self.outputs],
            'objects': [obj.serialize() for obj in self.objects]
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
    p.save('examples/add.json')
    p.load('examples/add.json')
    p[1].bang()
    p[0].bang()
    