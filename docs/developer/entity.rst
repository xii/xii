Entity
======

The entity class is a abstract class. It is inherited by any class which is
used in `xii`.

Following classes inheriting `Entity`:

* Command
* Component
* Attribute

The hierachy resulting hierachy is the following:
::
    Command
      \
       '- [Components]
             \
              '- [Attributes]
                  |- maybe need classes
                  '- custom classes

*********
Reference
*********

.. autoclass:: xii.entity.Entity
   :members:
