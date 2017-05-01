from xii.validator import Bool

from xii.components.node import NodeAttribute


class GraphicAttribute(NodeAttribute):
    """Attach spice output to the created node.
    By simply adding the graphich line xii is instructed to add a vnc spice
    connection to the started node.

    Currently only qxl/spice output is supported.
    """
    atype = "graphic"
    keys = Bool(True)
    defaults = True

    example = """
    # vim: set ts=2 sw=2 tw=0 ft=yaml:
    ---
    with-graphic:
    type: node
    pool: default

    image: {{ image }}

    graphic: yes
  """

    def spawn(self):
        if not self.settings():
            return
        xml = self.template('graphic.xml')
        self.add_xml('devices', xml.safe_substitute())
