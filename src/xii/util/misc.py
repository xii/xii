import hashlib

from Crypto.PublicKey import RSA
from concurrent.futures import ThreadPoolExecutor, Future
from functools import partial


def create_xml_node(name, attrs={}, text=""):
    """create a xml node with optional attributes

    > create_xml_node("test", {"foo": "bar"}, "some text")
    <test foo="bar">some text</test>

    Args:
        name:    name of the node
        attrs:   additional attributes for the node
        text:    text between opening/closing tag

    Returns:
        A xml node as string
    """
    attrs_xml = " ".join(map(lambda v: "{}=\"{}\"".format(*v), attrs.items()))
    return "<{} {}>{}</{}>".format(name, attrs_xml, text, name)


def safe_get(name, structure):
    if name not in structure:
        return None
    return structure[name]


def md5digest(input):
    return hashlib.md5(input.encode("utf-8")).hexdigest()


def generate_rsa_key_pair():
    rsa = RSA.generate(4096)
    pub = rsa.publickey()
    return (rsa.exportKey("PEM"), pub.exportKey("OpenSSH"))


def flatten(to_flatten):
    x = []
    if isinstance(to_flatten, list):
        for i in to_flatten:
            x = x + flatten(i)
        return x
    return [to_flatten]


def in_parallel(worker_count, objects, executor):
    try:
        pool = ThreadPoolExecutor(worker_count)
        futures = list(map(partial(pool.submit, executor), objects))

        # handle possible errors
        errors = list(filter(None, map(Future.exception, futures)))

        if errors:
            for err in errors:
                raise err
        return map(Future.result, futures)
    finally:
        pool.shutdown(wait=False)


def indented(lx, n):
    if not isinstance(lx, list):
        return (" " * n) + lx
    # FIXME: Make generator after debugging
    x = []
    for l in lx:
        x.append( (" " * n) + l)
    return x
