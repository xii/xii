import os

from xii.validator import String
from xii.components.pool import PoolAttribute


class DirectoryAttribute(PoolAttribute):
    atype = "directory"
    pool_type = "dir"
    keys = String()

    def validate(self):
        PoolAttribute.validate(self)

        if not os.path.isabs(self.settings()):
            raise error.ValidatorError("{} needs to be a valid absolut path."
                                       .format(self.entity()))

    def spawn(self):
        tpl = self.template("directory.xml")

        self.add_xml(tpl.safe_substitute({
            "path": self.settings()
        }))

    def after_spawn(self):
        pool = self.get_pool(self.component_entity())

        if not os.path.exists(self.settings()):
            pool.build()
