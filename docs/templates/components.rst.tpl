Documentation
====================

.. toctree::
   :maxdepth: 2

   components

Definition file
^^^^^^^^^^^^^^^

To define a environment one file is used. This file is structured in yaml format
and called definition file (file type extension is `.xii`).

xii assumes that the definition file is named like the parents directory.
::

  example/
    |---- example.xii
    '---- ...

but you can also use a another name and use the commandline option `-D` directly
point to definiton file.

A simple defintion file could be look like this:

.. code-block:: yaml
   :linenos:

   # vim: set ts=2 sw=2 tw=0 ft=yaml:
   ---
   single:
     type: node
     network:
       source: default
       ip: 192.168.122.112
     pool: default
     image: {{ "{{" }} image {{ "}}" }}
 
     graphic: yes
     user:
       linuxuser:
         password: linux
       root:
         password: linux
     ssh:
       copy-key:
         users:
           - linuxuser
           - root


Each component describes a role to be created. For instance `node` creates a
new virtual machine and network a virtual network. Every component can be described
by one or more `attributes` which define a property or action which should performed.

Checkout all currently implemented component types:

.. toctree::
  :maxdepth: 1

{% for item in toc %}
  {{ item }}
{% endfor %}

Attribute Definition
^^^^^^^^^^^^^^^^^^^^

Variables and System Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

xii can inject information into the running system using a simple templating
mechanism:
::

  # for expressions (variables)
  test:
    type: node
    image: {{ "{{" }} image {{ "}}" }}
    ...

  # for statements{% raw %}
  {% for names in all_name %}
  {{ name }}:
    type: node
    image: {{ image }}
    ...
  {% endfor %}
  {% endraw %}

  # for conditionals{% raw %}
  {% if enable_haproxy %}
  haproxy:
    type: node
    image: {{ image }}
    ...
  {% endif %}
  {% endraw %}

Variables can be injected using the `-D` switch:
::
  
  xii -Dimage=/path/to/image -Duser=testuser start

or via environment variables
::

  export XII_image="/path/to/image"
  export XII_user="testuser"
  xii start
