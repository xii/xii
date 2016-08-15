import inspect

from xii import error
from xii.output import debug
from xii.ui import HasOutput


class Entity(HasOutput):
    entity = "entity"
    name = "name"

    toplevel = False
    requires = []
    needs = []

    _childs = []
    _shares = {}

    def __init__(self, name, runtime=None, parent=None):
        if parent and self.toplevel:
            raise error.Bug("{} is a toplevel entity but added "
                            "as child?".format(self.entity))

        self.name = name
        self._parent = parent
        self._runtime = runtime

    def full_name(self):
        if self._parent:
            return self._parent.full_name() + [self.name]
        return [self.name]

    def add(self, new):
        for idx, child in enumerate(self._childs):
            if child.entity == new.entity:
                self._childs[idx] = new
                return
        self._childs.append(new)

    def get_child(self, name):
        for child in self._childs:
            if child.name == name:
                return child
        return None

    def get_parent(self):
        if self._parent is None:
            raise error.Bug("{} is trying to get parent entity, but there "
                            "is none".format(self.entity))
        return self._parent

    def get_runtime(self):
        if self._parent is not None:
            return self._parent.get_runtime()
        return self._runtime

    def get_ui(self):
        return self.get_runtime()["userinterface"]

    def get_config(self):
        return self.get_runtime()["config"]

    def get_virt_url(self):
        dfn = self.get_runtime()["definition"]
        return dfn.settings("connection", self.get_config().default_host())

    def run(self, action):
        if action in dir(self):
            getattr(self, action)()

    def childs_run(self, action):
        for child in self._childs:
            child.run(action)

    def validate(self):
        self._reorder_childs()
        for required in self.requires:
            child = self.get_child(required)
            if not child:
                raise error.NotFound("Could not find required `{}` "
                                     "in {}".format(required, self.name))
            child.validate()

        if self._parent:
            for parent in self.needs:
                if parent == self._parent.entity:
                    return
            raise error.NotFound("{} can only used as configuration "
                                 "for {}".format(self.entity, ",".join(self.needs)))

    def share(self, name, creator, finalizer=None):
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
                    debug("Requirement {} does not exist".format(requirement))
                    continue

                if move > idx:
                    self._childs.insert(idx, self._childs.pop(move))
                    has_moved = True
            if not has_moved:
                idx += 1
            rounds += 1


class EntityRegister():
    _registered = {
        'component': {},
        'attribute': {}
    }

    @classmethod
    def register(cls, group, klass):
        if Entity not in inspect.getmro(klass):
            raise error.Bug("{} is not a entity".format(klass.__name__))

        if klass.entity in cls._registered[group]:
            raise error.Bug("{}/{} is already defined".format(group, klass.entity))
        cls._registered[group][klass.entity] = klass

    @classmethod
    def get_entity(cls, group, name):
        if name not in cls._registered[group]:
            raise error.NotFound("Could not find `{}/{}`. Maybe misspelled?".format(group, name))
        return cls._registered[group][name]
