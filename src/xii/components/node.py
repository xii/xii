from xii.component import Component, ComponentRegister
from xii.property import Property, PropertyRegister

class NodeComponent(Component):
    require_properties = ['image']

    def start(self):
        if self.is_ready():
            print("I would start the image now!")
        else:
            print("Missing required property")


class ImageProperty(Property):
    name = "image"
    allowed_components = "node"

    pass


ComponentRegister.register('node', NodeComponent)
PropertyRegister.register('image', ImageProperty)
