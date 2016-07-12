import time
import libvirt

from xii import error
from xii.output import fatal

def valid(domain):
    if not domain:
        return False
    return True

def has_state(domain, state):
    return domain.state()[0] == state

def wait_until(domain, state, timeout=5):
    for i in range(timeout):
        if has_state(domain, state):
            return True
        time.sleep(1)
    return False

def wait_active(domain, state=True, timeout=5):
    for i in range(timeout):
        if domain.isActive() == state:
            return True
        time.sleep(1)
    return False


def each(conn, names):
    for name in names:
        domain = conn.get_domain(name)

        if not valid(domain):
            fatal("Could not find domain {}". format(name))
            continue
        yield (name, domain)
