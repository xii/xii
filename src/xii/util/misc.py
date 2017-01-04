import md5
from Crypto.PublicKey import RSA

def safe_get(name, structure):
    if name not in structure:
        return None
    return structure[name]


def md5digest(input):
    return md5.new(input).hexdigest()


def generate_rsa_key_pair():
    rsa = RSA.generate(4096)
    pub = rsa.publickey()
    return (rsa.exportKey("PEM"), pub.exportKey("OpenSSH"))
