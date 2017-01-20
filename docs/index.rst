Documentation
=============

**Welome to the documentation website of the xii project.**

xii is a virtual environment manager. Complete environments can be defined in
just one file.

This website covers the projects enduser documentation and developer
instructions.

Installation
------------
Currently `xii` is currently not included in any distribution so the only
way to install is via `pip` or git repository.

Requirements:
^^^^^^^^^^^^^

To install `xii` via `pip`:
::

  pip install xii

or via the github repository:
::

  git clone https://github.com/xii/xii
  cd xii
  python setup.py install

System package requirements:

* `python` - a working python2.7 installation
* `libguestfs` - a working guestfs installation
* `libguestfs-python` - python 2 bindings for guestfs
* `libvirtd` - a working libvirt installation **+ qemu/kvm provider**
* `libvirtd-python` - python 2 bindings for guestfs

Python packages which are required:

* `paramiko` - the ssh library
* `pyYAML` - yaml parser
* `pycrypto` - various encrypthon standards
* `jinja2` - the templating library
* `futures` - parallel tasks execution

After successfully installed xii you can run the `xii check-installation` to
verify the installation. You can checkout examples here or start right away with
the Quickstart.


Quickstart
----------

Spawning a single instance is easy. Defining a new instance is done via a 
`yaml file`.
You can create a template definition file using the `create` command:
::

  $ xii create example --nodes 1
  FIXME: Add output
  cd example

Important is to set a valid `pool` and a `image` attribute, for more information
this could for example:
::

  ---
  single:
    type: node
    network: default
    pool: default
    image: https://xii-project.org/example/opensuse-leap-42.2.qcow2
    graphic: yes
    user:
      root:
        password: linux
    ssh:
      copy-key:
        users:
          - root

start the instance by typing:
::

  $ xii start
  FIXME: Add output

voila the instance is running. You can now connect trough ssh by typing:
::

  $ xii ssh
  FIXME: Add output

After testing or what ever you wanted to to:
::

  $ xii destroy

.. note::

  You can also `suspend`/`resume` the instance. If you want to use
  it later! Checkout Commands for more commands.

Happy hacking!


Further reading
---------------

.. toctree::
  :maxdepth: 2

  commands
  components
  configuration
  developer
