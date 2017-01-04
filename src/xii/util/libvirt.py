import time

def wait_until_active(obj, state=1, timeout=5):
    for _ in range(timeout):
        if obj.isActive() == state:
            return True
        time.sleep(1)
    return False


def wait_until_inactive(obj, state=0, timeout=5):
    return wait_until_active(obj, state, timeout)


def domain_has_state(domain, state):
    return domain.state()[0] == state


def domain_wait_state(domain, state, timeout=5):
    for _ in range(timeout):
        if domain_has_state(domain, state):
            return True
        time.sleep(1)
    return False
