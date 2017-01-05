import socket

from xii import error, util


# sample validator
# keys = Dict(
#     [
#         RequiredKey("foo", String(), desc="A string to manipulate something"),
#         Key("bar", String(), desc="something usefull")
#     ],
#     desc="Implement this stuff as you want"
# )
class Desc():
    desc = "undocumented"

    def __init__(self, desc=None):
        if desc is not None:
            self.desc = desc


class TypeCheck(Desc):
    want_type = None
    want = "none"

    def __init__(self, desc=None):
        if desc is None:
            Desc.__init__(self, self.want_type)
        else:
            Desc.__init__(self, desc)

    def validate(self, pre, structure):
        if isinstance(structure, self.want_type):
            return True
        raise error.ValidatorError("{} needs to be {}".format(pre, self.want))
        return False


class Int(TypeCheck):
    want = "int"
    want_type = int


class Bool(TypeCheck):
    want = "bool"
    want_type = bool


class String(TypeCheck):
    want = "string"
    want_type = basestring


class Ip(TypeCheck):
    want = "ip"
    want_type = basestring

    def validate(self, pre, structure):
        TypeCheck.validate(self, pre, structure)

        try:
            socket.inet_pton(socket.AF_INET, structure)
            return True
        except socket.error:
            try:
                socket.inet_pton(socket.AF_INET6, structure)
                return True
            except socket.error:
                pass
        raise error.ValidatorError("{} is not a valid IP address".format(pre))

class List(TypeCheck):
    want = "list"
    want_type = list

    def __init__(self, schema, desc=None):
        TypeCheck.__init__(self, desc)
        self.schema = schema

    def validate(self, pre, structure):
        TypeCheck.validate(self, pre, structure)

        def _validate_each(item):
            return self.schema.validate(pre, item)
        return sum(map(_validate_each, structure)) > 1


class Or(Desc):
    def __init__(self, schemas, desc=None, exclusive=True):
        Desc.__init__(self, desc)
        self.schemas = schemas
        self.exclusive = exclusive

    def validate(self, pre, structure):
        errors = []

        def _validate_each(schema):
            try:
                return schema.validate(pre, structure)
            except error.ValidatorError as err:
                errors.append(err)
                return False

        state = sum(map(_validate_each, self.schemas))

        if self.exclusive and (state > 1 or state == 0):
            def _error_lines():
                it = iter(errors)
                yield " ".join(next(it).error())
                for err in it:
                    yield "or"
                    yield " ".join(err.error())
            raise error.ValidatorError(["{} is ambigous:".format(pre)] +
                                       list(_error_lines()))
        return True


class VariableKeys(Desc):
    def __init__(self, schema, desc=None):
        Desc.__init__(self, desc)
        self.schema = schema

    def validate(self, pre, structure):

        if not isinstance(structure, dict):
            raise error.ValidatorError("{} needs to be a dict".format(pre))

        def _validate_each(pair):
            (name, next_structure) = pair
            return self.schema.validate(pre + " > " + name, next_structure)
        return sum(map(_validate_each, structure.items())) >= 1


class Key(Desc):
    def __init__(self, name, schema, desc=None):
        Desc.__init__(self, desc)
        self.name = name
        self.schema = schema

    def validate(self, pre, structure):
        if not isinstance(structure, dict):
            raise error.ValidatorError("{} needs to be a dict".format(pre))
        value_of_key = util.safe_get(self.name, structure)
        if not value_of_key:
            return False
        return self.schema.validate(pre + " > " + self.name, value_of_key)


class RequiredKey(Desc):
    def __init__(self, name, schema, desc=None):
        Desc.__init__(self, desc)
        self.name = name
        self.schema = schema

    def validate(self, pre, structure):
        value_of_key = util.safe_get(self.name, structure)
        if not value_of_key:
            raise error.ValidatorError("{} must have {} "
                                       "defined".format(pre, self.name))
        return self.schema.validate(pre + " > " + self.name, value_of_key)


class Dict(TypeCheck):
    want = "dictonary"
    want_type = dict

    def __init__(self, schemas, desc=None):
        TypeCheck.__init__(self, desc)
        self.schemas = schemas

    def validate(self, pre, structure):
        TypeCheck.validate(self, pre, structure)

        def _validate(schema):
            return schema.validate(pre, structure)
        return sum(map(_validate, self.schemas)) >= 1
