from errors.interpreter_errors import UnexpectedTypeError


class PrintFun:
    name = "print"

    def accept(self, _, *args):
        args = [self.to_string(arg) for arg in args]
        print(*args)

    @staticmethod
    def to_string(arg):
        if arg is None:
            return "null"
        if arg is True:
            return "true"
        if arg is False:
            return "false"
        return str(arg)


class Int:
    name = "int"

    def accept(self, _, value):
        if isinstance(value, (int, float, str)):
            try:
                return int(value)
            except ValueError:
                raise UnexpectedTypeError("int()", position=None)
        raise UnexpectedTypeError("int()", position=None)


class Float:
    name = "float"

    def accept(self, _, value):
        if isinstance(value, (int, float, str)):
            try:
                return float(value)
            except ValueError:
                raise UnexpectedTypeError("float()", position=None)
        raise UnexpectedTypeError("float()", position=None)


class Bool:
    name = "bool"

    def accept(self, _, value):
        return bool(value)


class Str:
    name = "str"

    def accept(self, _, value):
        return str(value)


class ToUpper:
    name = "toUpper"

    def accept(self, _, value):
        if isinstance(value, str):
            return value.upper()
        raise UnexpectedTypeError("toUpper()", position=None)


class ToLower:
    name = "toLower"

    def accept(self, _, value):
        if isinstance(value, str):
            return value.lower()
        raise UnexpectedTypeError("toLower()", position=None)