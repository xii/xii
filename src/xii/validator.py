from socket import inet_pton, AF_INET, AF_INET6

from xii import error, util


class TypeCheck():
    want_type = None
    want = "none"

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
            inet_pton(AF_INET, structure)
            return True
        except socket.error:
            try:
                inet_pton(AF_INET6, structure)
                return True
            except socket.error:
                pass
        return False
            

class Required():
    def __init__(self, schema):
        self.schema = schema

    def validate(self, pre, structure):
        return self.schema.validate(pre, structure)


class List(TypeCheck):
    want = "list"
    want_type = list

    def __init__(self, schema):
        self.schema = schema

    def validate(self, pre, structure):
        TypeCheck.validate(self, pre, structure)

        def _validate_each(item):
            return self.schema.validate(pre, item)
        return sum(map(_validate_each, structure)) > 1


class Or():
    def __init__(self, schemas, exclusive=True):
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

        if self.exclusive and state > 1 or state == 0:
            def _error_lines():
                it = iter(errors)
                yield " ".join(next(it).error())
                for err in it:
                    yield "or"
                    yield " ".join(err.error())
            raise error.ValidatorError(["{} is ambigous:".format(pre)]
                                       + list(_error_lines()))
        return True


class VariableKeys():
    def __init__(self, schema):
        self.schema = schema

    def validate(self, pre, structure):
        def _validate_each(pair):
            (name, next_structure) = pair
            return self.schema.validate(pre + " > " + name, next_structure)
        return sum(map(_validate_each, structure.items())) >= 1


class Key():
    def __init__(self, name, schema):
        self.name = name
        self.schema = schema

    def validate(self, pre, structure):
        value_of_key = util.safe_get(self.name, structure)
        if not value_of_key:
            return True
        return self.schema.validate(pre + " > " + self.name, value_of_key)


class RequiredKey():
    def __init__(self, name, schema):
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

    def __init__(self, schemas):
        self.schemas = schemas

    def validate(self, pre, structure):
        TypeCheck.validate(self, pre, structure)

        def _validate(schema): 
            return schema.validate(pre, structure)
        return sum(map(_validate, self.schemas)) == len(self.schemas)
