import inspect

from xii import error, util
from xii.output import HasOutput

class Entity(HasOutput):
    requires = []

    def __init__(self, name, store=None, parent=None):
        self._entity = name
        self._parent = parent
        self._store = store
        self._childs = []
        self._shares = {}

    def has_parent(self):
        return self._parent is not None

    def parent(self):
        if not self.has_parent():
            raise error.Bug("{} is trying to get parent entity, but there "
                            "is none".format(self.entity()))
        return self._parent

    def entity_path(self):
        if self.has_parent():
            return self._parent.entity_path() + [self._entity]
        return [self._entity]

    def entity(self):
        return self._entity

    def store(self):
        import pdb; pdb.set_trace()
        return self._store

    def validate(self, required_children=None):
        self._reorder_childs()
        if required_children:
            for required in required_children:
                child = self.get_child(required)
                if not child:
                    raise error.NotFound("Could not find required `{}` "
                                        "in {}".format(required, self.name))
        for child in self._childs:
            child.validate()

    def share(self, name, creator, finalizer=None):
        if self.has_parent():
            return self.get_parent().share(name, creator, finalizer)

        if name not in self._shares:
            self._shares[name] = {
                "value": creator(),
                "finalizer": finalizer
            }
        return self._shares[name]['value']

    def finalize(self):
        for name, shared in self._shares.items():
            if shared["finalizer"] is not None:
                shared["finalizer"](shared['value'])
            del self._shares[name]

    def run(self, action):
        if action in dir(self):
            getattr(self, action)()

    def add_child(self, new):
        for idx, child in enumerate(self._childs):
            if child.entity() == new.entity():
                self._childs[idx] = new
                return
        self._childs.append(new)

    def get_child(self, name):
        for child in self._childs:
            if child.name == name:
                return child
        return None

    def children(self):
        return self._childs

    def each_child(self, action, reverse=False):
        if reverse:
            run = reversed(self._childs)
        else:
            run = self._childs

        for child in run:
            child.run(action)

    def _child_index(self, name):
        for idx, child in enumerate(self._childs):
            if child.name == name:
                return idx
        return None

    def _reorder_childs(self):
        idx = 0
        rounds = 0
        size = len(self._childs)

        while idx != size:
            has_moved = False
            if rounds > size * 2:
                raise error.Bug("Cyclic dependencies.")

            for requirement in self._childs[idx].requires:
                move = self._child_index(requirement)
                if move is None:
                    continue

                if move > idx:
                    self._childs.insert(idx, self._childs.pop(move))
                    has_moved = True
            if not has_moved:
                idx += 1
            rounds += 1


    # def get_virt_url(self):
    #     dfn = self.get_runtime()["definition"]
    #     return dfn.settings("connection", self.get_config().default_host())


class EntityRegister():
    _registered = {
        'component': {},
        'attribute': {}
    } 

    @classmethod
    def register_component(cls, klass):
        print("registering component {}".format(klass.__name__))
        if Entity not in inspect.getmro(klass):
            raise error.Bug("{} is not a entity".format(klass.__name__))

        if klass.entity in cls._registered["component"]:
            raise error.Bug("{}/{} is already defined"
                            .format("component", klass.entity))

        cls._registered["component"][klass.ctype] = klass

    @classmethod
    def register_attribute(cls, component, klass):
        print("registering attribute {}/{}".format(component, klass.__name__))
        if Entity not in inspect.getmro(klass):
            raise error.Bug("{} is not a entity".format(klass.__name__))

        if component not in cls._registered["attribute"]:
            cls._registered["attribute"][component] = {}

        if klass.entity in cls._registered["attribute"][component]:
            raise error.Bug("{}/{}/{} is already defined"
                            .format("attribute", component, klass.entity))

        cls._registered["attribute"][component][klass.attr_type] = klass

    @classmethod
    def get_component(cls, ctype):
        if ctype not in cls._registered["component"]:
            raise error.NotFound("Unknown component `{}`. Maybe misspelled?".format(ctype))
        return cls._registered["component"][ctype]

    @classmethod
    def get_attribute(cls, ctype, aname):
        if (ctype not in cls._registered["attribute"] or 
            aname not in cls._registered["attribute"][ctype][aname]):
            raise error.NotFound("Unkown attribute `{}`. "
                            "Maybe misspelled?".format(aname, ctype))
        return cls_registered["attribute"][ctype][aname]
