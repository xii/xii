import md5

from Crypto.PublicKey import RSA
from concurrent.futures import ThreadPoolExecutor, Future
from functools import partial


def create_xml_node(name, attrs={}, text=""):
    """create a xml node with optional attributes

    > create_xml_node("test", {"foo": "bar"}, "some text")
    <test foo="bar">some text</test>

    Args:
        name    name of the node
        attrs   additional attributes for the node
        text    text between opening/closing tag

    Returns:
        A xml node as string
    """
    attrs_xml = " ".join(map(lambda v: "{}=\"{}\"".format(*v), attrs.items()))
    return "<{} {}>{}</{}>".format(name, attrs_xml, text, name)


def default(key, struct, default=None):
    """return value or if key not exists default
    value

    Args:
        key     key to search for
        struct  structure (dict) to search key in
        default default value if key is not found

    Returns:
        value of key or default
    """
    if key not in struct:
        return default
    return struct[key]


def md5digest(input):
    """generate a md5 digest of a input string

    Args:
        input   input which should be hashed

    Returns:
        The md5 hash sum
    """
    return md5.new(input).hexdigest()


def generate_rsa_key_pair():
    """generate a new rsa key pair

    Returns:
        A tuple which (private, public) keys
    """
    rsa = RSA.generate(4096)
    pub = rsa.publickey()
    return (rsa.exportKey("PEM"), pub.exportKey("OpenSSH"))


def flatten(to_flatten):
    """reduce list in lists to one list
    eg. [[]] -> []
    or  [[[]]] -> []

    Args:
        to_flatten  list structure which should reduced

    Returns:
        The reduced list
    """
    x = []
    if isinstance(to_flatten, list):
        for i in to_flatten:
            x = x + flatten(i)
        return x
    return [to_flatten]


def in_parallel(worker_count, objects, executor):
    """execute a function in parallel

    Args:
        worker_count    how many threads should be created
        objects         objects which should be worked on
        executor        function which takes a object to work on

    Returns:
        The result of the executor functions as list

    Raises:
        Raises all exception wich are occured in the executor
        function
    """
    try:
        pool = ThreadPoolExecutor(worker_count)
        futures = map(partial(pool.submit, executor), objects)

        # handle possible errors
        errors = filter(None, map(Future.exception, futures))

        if errors:
            for err in errors:
                raise err
        return map(Future.result, futures)
    finally:
        pool.shutdown(wait=False)
