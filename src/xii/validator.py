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


def ins(str, indent):
    return [util.indented(str, indent)]

class Validator():
    def __init__(self, description, example=None):
        self._description = description

    def example(self):
        return None

    def description(self, indent=0):
        return self._description


class TypeCheck(Validator):
    want_type = None
    want = "none"

    def __init__(self, desc=None):
        if desc is None:
            Validator.__init__(self, self.want)
        else:
            Validator.__init__(self, desc)

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

    def description(self, indent=0):
        return [self.schema.description()]
        # desc = self.schema.description(0)
        # if isinstance(desc, list):
        #     return ["["] + desc + ["]"]
        # else:
        #     return "[" + desc + "]"


class Or(Validator):
    def __init__(self, schemas, desc=None, exclusive=True):
        Validator.__init__(self, desc)
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

    def description(self, indent=0):
        def add(desc, x):
            if isinstance(x, list):
                map(desc.append, x)
            else:
                desc.append(x)

        desc = []
        descs = [ s.description(0) for s in self.schemas ]

        for d in descs[:-1]:
            add(desc, d)
            desc.append("__or__")
        add(desc, descs[-1])
        return desc


# Key validators --------------------------------------------------------------

class KeyValidator(Validator):
    key_desc = "{}"

    def description(self, indent=0):
        return (self.key_desc.format(self.name), self.schema.description())
        # key = self.key_desc.format(self.name)
        # desc = util.flatten(self.schema.description(indent=0))

        # if len(desc) == 1:
        #     return key + desc[0]

        # desc[0] = key + desc[0]
        # return desc

class VariableKeys(KeyValidator):

    def __init__(self, schema, desc=None, example=None):
        KeyValidator.__init__(self, desc, example)
        self.name = "*"
        self.schema = schema

    def validate(self, pre, structure):

        if not isinstance(structure, dict):
            raise error.ValidatorError("{} needs to be a dict".format(pre))

        def _validate_each(pair):
            (name, next_structure) = pair
            return self.schema.validate(pre + " > " + name, next_structure)
        return sum(map(_validate_each, structure.items())) >= 1
        return ins("`variable keys`:", indent) + desc


class Key(KeyValidator):

    def __init__(self, name, schema, desc=None, example=None):
        KeyValidator.__init__(self, desc, example)
        self.name = name
        self.schema = schema

    def validate(self, pre, structure):
        if not isinstance(structure, dict):
            raise error.ValidatorError("{} needs to be a dict".format(pre))
        value_of_key = util.safe_get(self.name, structure)
        if not value_of_key:
            return False
        return self.schema.validate(pre + " > " + self.name, value_of_key)


class RequiredKey(KeyValidator):

    def __init__(self, name, schema, desc=None, example=None):
        Validator.__init__(self, desc, example)
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

    def description(self, indent=0):
        desc_dict = {}
        for key, value in [s.description() for s in self.schemas]:
            desc_dict[key] = value
        return desc_dict
        # desc = ["{"]

        # for s in self.schemas:
        #     d = util.flatten(s.description(indent=0))
        #     map(desc.append, util.flatten(s.description(indent=0)))

        # return desc + ["}"]
