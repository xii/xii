# mkcrowbar — Easy crowbar installation on SUSE hosts
A __unofficial__ installation script for the crowbar project on modern SUSE based hosts (SLES >= 12).
It bootstraps crowbar and makes neccessary preperations (configure network, enable repositories)

## Installation
Before start installing. Get the latest python3 runtime. (Available as repository here: [openSUSE Build Service](http://download.opensuse.org/repositories/devel:/languages:/python3/))

    zypper in python3 python3-pip

Download and install the script:

    git clone https://github.com/felixsch/mkcrowbar.git
    cd mkcrowbar
    pip3 install -r requirements.txt
    sudo python3 setup.py install
    
## Running the script
```
Usage:
    mkcrowbar [SWITCHES] [SUBCOMMAND [SWITCHES]] [conf=None]

Meta-switches
    -h, --help             Prints this help message and quits
    --help-all             Print help messages of all subcommands and quit
    --version              Prints the program's version and quits

Switches
    --non-interactive      Non interactive output; Usefule if used in scripts
    -v, --verbose          Show verbose output

Subcommands:
    checks                 Check if everything is ready to bootstrap crowbar
    install                Install crowbar on this maschine
    prepare                Prepare host for crowbar installation
    repos                  Configures the install repos for crowbar clients
    setup                  bootstrap and configure crowbar
```
You can run all steps at once by omitting the subcommand

    mkcrowbar example-env.yaml

The order is: install, prepare, checks, repos, setup.


## configure the environment
The complete installation environment is defined in a yaml file.

_NOTE:_ This example file can be found in `examples`

```
# The SUSE product your want to install
product: storage

# example-env.yaml
# Specify a fully qualified hostname for the admin node
hostname: crowbar.suse.com

# Sets the timezone if the timezone is not yet set
timezone: Europe/Berlin

# Specify which network interface to use for the admin network
interface: eth1

# Just check if the ip is correct. Do not update configuration or check if ip is
# static
only-checks: False

# network configuration for the crowbar host. You can set settings according to
# the Interface Configuration Files. 
# HINT: If you want to use ipv6, you need to set NETWORKING_IPV6 in /etc/sysconfig/network
network:
    ipaddr: 192.168.124.10                      
    broadcast: 192.168.124.255
    mtu: 1500
    netmask: 255.255.255.0
    #ipv6init: yes
    #ipv6addr: 2607:f0d0:1002:0011:0000:0000:0000:0002
    #ipv6_defaultgw: 2607:f0d0:1002:0011:0000:0000:0000:0001

# Configure repositories via zypper
use-zypper: true
# Define installation medias from where to install crowbar
# - <URL>.repo
# or if not repo file available:
# - alias:
#     repo : URL | path
#     type : yast2 | rpm-md | plaindir
#     ... (all settings vailable in zypper)
install-media:
    - https://repo/url/to/product.repo
    - https://repo/url/to/another/product/you/want/to/activate.repo
    - some-rpm-md-repo:
        repo: URL or path to device/mount

# Extra components to install
# Currently supported: core (installed anyway), ceph, ha, hyperv, openstack
crowbar-components:
  - core
  - ceph

# TFTP repositories which should be available from crowbar within the network
# various modes are available:
# nfs - Mount repository data as a nfs share
#   name: <name>                Name of the repository (e.g install)
#   type: nfs                   Nfs mount
#   version: <version>          Server version (e.g suse-12.1 or suse-12.0)
#   source: <nfs server share>  Source of the nfs share
#
# createrepo - Create a empty repo (for use with SUSE Manager)
#   NOTE: You need to sign the repository manually
#   name: <name>                Name of the repository (e.g install)
#   type: createrepo            Create empty repository
#   version <version>           Server version (e.g suse-12.1 or suse.12.0)
#   tag: <tag>                  Tag for this repository (optional)

# For a correct installation you minimal configuration should provide a install repository,
# the pool and update repository for your server version and the product repository (cloud or storage)
repositories:
  - name: install
    type: nfs
    version: suse-12.0
    source: somehost:/data/repos/sle-12/dvd1

  - name: Cloud
    type: nfs
    version: suse-12.0
    source: somehost:/data/repos/cloud-6/dvd1

  - name: SLES12-Pool
    type: nfs
    version: suse-12.0
    source: somehost:/data/repos/sle-12-pool

  - name: SLES12-Updates
    type: nfs
    version: suse-12.0
    source: somehost:/data/repos/sle-12-update
```

# Disclaimer
This is alpha state software. Do not use it in production environment.
