Command
=======

Add a new subcommand to xii.

Xii is built upon commands which call components and attributes to do
some specific task.

The general directory syntax is the following:
::

    path/
    '---- command/
          |---- python_files.py
          |---- ...
          |---- __init__.py
          '---- templates/
                |---- templates_files.xml
                '---- ...

The __init__.py file should export the added command and nothing
else. You can export more than one at once if you like. In general
each command should be in its own directory.

.. code-block:: python
    :linenos:

    class InfoCommand(Command):
        name = ["info", "i"]
        help = "print some infos about xii"

        def argument_parser(self):
            parser = Command.argument_parser(self)
            parser.add_argument("--more-infos", default=None,
                                help="A argument")
            return parser

        def run(self):
            self.say("do something")
            self.each_component("info")
            self.say(self.args().more_infos)


*********
Reference
*********
.. autoclass:: xii.command.Command
   :members:
