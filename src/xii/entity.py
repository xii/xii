import inspect

from multiprocessing import Lock

from xii import error
from xii.ui import HasOutput


class Entity(HasOutput):
    entity = "entity"
    name = "name"

    toplevel = False
    requires = []


    def __init__(self, name, runtime=None, parent=None):
        if parent and self.toplevel:
            raise error.Bug("{} is a toplevel entity but added "
                            "as child?".format(self.entity))

        self.name = name
        self._parent = parent
        self._runtime = runtime
        self._childs = []
        self._shares = {}

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

    def get_definition(self):
        return self.get_runtime()["definition"]

    def get_virt_url(self):
        dfn = self.get_runtime()["definition"]
        return dfn.settings("connection", self.get_config().default_host())

    def run(self, action):
        if action in dir(self):
            getattr(self, action)()

    def childs_run(self, action, reverse=False):
        if reverse:
            run = reversed(self._childs)
        else:
            run = self._childs

        for child in run:
            child.run(action)

    def validate(self):
        self._reorder_childs()
        for required in self.requires:
            child = self.get_child(required)
            if not child:
                raise error.NotFound("Could not find required `{}` "
                                     "in {}".format(required, self.name))
            child.validate()

    def share(self, name, creator, finalizer=None):
        if name not in self._shares:
            self._shares[name] = {
                "value": creator(),
                "finalizer": finalizer
            }
        return self._shares[name]['value']

    def global_share(self, key, value=None, default=None):
        runtime = self.get_runtime()

        # if set a new value
        if value is not None:
            runtime['share'][key] = value

        # if key does not exist, create new one
        if key not in runtime["share"]:
            runtime["share"][key] = default

        return runtime["share"][key]

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
    def register_component(cls, klass):
        if Entity not in inspect.getmro(klass):
            raise error.Bug("{} is not a entity".format(klass.__name__))

        if klass.entity in cls._registered["component"]:
            raise error.Bug("{}/{} is already defined"
                            .format("component", klass.entity))

        cls._registered["component"][klass.entity] = klass

    @classmethod
    def register_attribute(cls, component, klass):
        if Entity not in inspect.getmro(klass):
            raise error.Bug("{} is not a entity".format(klass.__name__))

        if component not in cls._registered["attribute"]:
            cls._registered["attribute"][component] = {}

        if klass.entity in cls._registered["attribute"][component]:
            raise error.Bug("{}/{}/{} is already defined"
                            .format("attribute", component, klass.entity))

        cls._registered["attribute"][component][klass.entity] = klass

    @classmethod
    def get_entity(cls, name, group, component=None):
        if component is None:
            if name not in cls._registered[group]:
                raise error.NotFound("Could not find `{}/{}`. "
                                     "Maybe misspelled?".format(group, name))

            return cls._registered[group][name]

        if component not in cls._registered[group]:
            raise error.DefError("Could not find `{}/{}/{}`. Maybe misspelled?"
                                 .format(component, group, name))

        if name not in cls._registered[group][component]:
            raise error.DefError("Could not find `{}/{}/{}`. Maybe misspelled?"
                                 .format(component, group, name))

        return cls._registered[group][component][name]
