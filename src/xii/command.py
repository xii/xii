import argparse
import uuid

from concurrent.futures import ThreadPoolExecutor, Future
from functools import partial
from abc import ABCMeta, abstractmethod

from xii import error
from xii.store import HasStore
from xii.entity import Entity


# move me to util if time is ready
def in_parallel(worker_count, objects, executor):
    try:
        pool = ThreadPoolExecutor(worker_count)
        futures = map(partial(pool.submit, executor), objects)

        # handle possible errors
        errors = filter(None, map(Future.exception, futures))

        if errors:
            for err in errors:
                raise err
    finally:
        pool.shutdown(wait=False)


class Command(Entity, HasStore):
    __meta__ = ABCMeta

    name = None
    """
    Each command can called by more than one name. For example a command can be
    called by "start" and "s" as shorthand command.
    The first name is the name how to command should be named (full name)
    """

    help = None
    """
    Define a short help to make usage output more informative
    """

    def __init__(self, args, tpls, store):
        Entity.__init__(self, self.name[0], store, parent=None, templates=tpls)
        self._args = args

    # store() is already defined by Entity

    @abstractmethod
    def run(self):
        """Run the command
        Every command **must** implement the `run` method. This method
        is called after the commandline argument hast parsed

        Returns:
            Nothing is returned. If an error is occurred throw an appropriate
            exception
        """
        pass

    def add_component(self, component):
        """Adds a new component to the command.

        Args:
            component: The component object which should be added.

        Returns:
            Nothing is returned

        .. note:: This method does not check if the added object is a compatible component.
        """
        self.add_child(component)

    def get_component(self, name):
        """Get a component object

        Args:
            name: The entity name of the component.

        Returns:
            The component object if found, None otherwise
        """
        return self.get_child(name)

    def each_component(self, action, reverse=False):
        """Run a action on all added components
        This command can run a action (method) on each child. If parallel
        execution is enabled actions are exectuted on each component group
        in parallel.

        Args:
            action: The name of the action (method)
            reverse: if the component groups should be exectued in reverse order

        Returns:
            Nothing
        """
        try:
            if reverse:
                groups = reversed(self._grouped_components())
            else:
                groups = self._grouped_components()

            if self.get("global/parallel", True):
                count = self.get("global/workers", 3)
                for name, group in groups:
                    self.say("{}ing {}s..".format(action, name))
                    in_parallel(count, group, lambda o: o.run(action))
            else:
                self.each_child(action, reverse)
        except KeyboardInterrupt:
            raise error.Interrupted()

    @classmethod
    def argument_parser(cls):
        """Add special arguments to a subcommand
        Overwrite this method if additional arguments for the subcommand
        should be parsed.

        .. code-block:: python

            ...
            def argument_parser(cls):
                parser = Command.argument_parser(cls)
                parser.add_argument("--info", default="Foo",
                                 help="A helpful message")
                return parser

        For more informations about the argument parser checkout :mod:`argparse`.

        Returns:
            The parser object
        """
        parser = argparse.ArgumentParser(prog="xii " + cls.name[0])
        parser.add_argument("--verbose", action="store_true", default=None,
                            help="Show verbose output")
        return parser

    def args(self):
        """
        Get the parsed subcommand arguments (generated by `argument_parser`)

        Returns:
            The parsed subcommand arguments
        """
        return self._args

    def get_temp_dir(self):
        """ Get the temp path for this command

        You must take care that the directory actually exists
        on your host

        Returns:
            The temp path
        """
        if not self._temp_hash:
            self._temp_hash = "xii-" + self.entity() + "-" + str(uuid.uuid4())
        return os.path.join("/var/lib/tmp", self._temp_hash)

    def child_index(self, component):
        for idx, child in enumerate(self._childs):
            if child.ctype == component:
                return idx
        return None

    def _grouped_components(self):
        self.reorder_childs();
        groups = []
        childs = self.children()
        name = childs[0].ctype
        next = [childs[0]]

        for child in childs[1:]:
            if child.ctype == name:
                next.append(child)
            else:
                groups.append((name, next))
                name = child.ctype
                next = [child]
        groups.append((name, next))
        return groups
