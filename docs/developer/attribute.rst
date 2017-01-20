Attribute
=========

Each component can has more than one attributes which describe a specific task.
When a subcommand is called (eg. "start") the component triggeres the
corresponding action (in case of "start" it could be `spawn` and `start`).

If a action is not implemented by the attribtue the attribute is skipped. When
adding new attributes, the structure is the following:
::

    path/
    '---- component
          |---- attribute
                |---- python_files.py
                |---- ...
                |---- __init__.py
                '---- templates/
                      |---- template_file.py
                      '---- ...


The __init__.py file should export the attributes to export. This can be more
than one attribute at once. Usual every attribute should be contained in a
seperate directory.


.. code-block:: python
   :linenos:

   from xii.attribute import Attribute
   from xii.need import NeedGuestFS
 
   class SomeAttribute(Attribute, NeedGuestFS):
       atype="some"
       defaults={
               "some": "some text",
               "foo": "bar"
           }
       
       keys = Or([
           Dict([
               RequiredKey("some", String())
               Key("foo", String())
           ]),
           String()
       ])
 
       def spawn(self):
           self.say("Adding a some text to a image") 
           self.guest().write("/etc/some", self._to_text())

       def _to_text(self):
           if isinstance(self.settings(), dict):
               return "some: " + self.settings()

           pieces = ["{}: {}".format(k, v) for k, v in self.settings().items()]
           return "\n".join(pieces)

*********
Reference
*********

.. seealso::

   Most basic functionality is not included in this class but in
   :ref:`xii.entity.Entity` from which `Attribute` inherits.

   Check `xii.entity.Entity` for more basic methods.

.. autoclass:: xii.attribute.Attribute
   :members:
