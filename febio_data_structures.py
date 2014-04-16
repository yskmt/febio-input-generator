
class febio_part:
    def __init__(self, _name, _number):
        self.name = _name
        self.number = _number
        self.elems = []
        self.fix_disp = None

class febio_face:
    def __init__(self, _name, _number):
        self.name = _name
        self.number = _number
        self.elems = []
        self.fix_disp = None
        self.shell = 0

class febio_edge:
    def __init__(self, _name, _number):
        self.name = _name
        self.number = _number
        self.elems = []
        self.fix_disp = None

class febio_node:
    def __init__(self, _name, _number):
        self.name = _name
        self.number = _number

        
class Tree:
    def __init__(self, _name):
        self.attributes = {}
        self.name = _name
        self.children = []


class febio_step:
    def __init__(self, _name):
        self.name = _name

class febio_loadcurve:
    def __init__(self, _id, _type, _extend):
        self.id = _id
        self.type = _type
        self.extend = _extend
