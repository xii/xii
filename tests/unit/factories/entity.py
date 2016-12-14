import factory

from xii import entity
from factories import StoreWithNode



class Entity(factory.Factory):
    class Meta:
        model = entity.Entity
    name = factory.Sequence(lambda n: "entity-{}".format(n))


class EntityWithStore(Entity):
    store = StoreWithNode()

class EntityWithChilds(Entity):
    store = StoreWithNode()
    
    class Params:
        child_count = 3

    @factory.post_generation
    def add_childs(self, create, **kwargs):
        childs = []
        for _ in range(self.child_count):
            childs.append(Entity(parent=self))
        self._childs = childs
        return [self] + childs
        

    
