# from errors.interpreter_errors import UnexpectedTypeError, InvalidArgsCountError
# from interpreter.environment import Environment
from abc import ABC, abstractmethod

from errors.interpreter_errors import UnexpectedTypeError


class BuiltInFunctionVisitor(ABC):
    @abstractmethod
    def visit_print(self, fun, *args):
        pass

    @abstractmethod
    def visit_int(self, fun, value):
        pass

    @abstractmethod
    def visit_float(self, fun, value):
        pass

    @abstractmethod
    def visit_bool(self, fun, value):
        pass

    @abstractmethod
    def visit_str(self, fun, value):
        pass

    @abstractmethod
    def visit_to_upper(self, fun, value):
        pass

    @abstractmethod
    def visit_to_lower(self, fun, value):
        pass


class BuiltInFunction:
    def accept(self, visitor, *args):
        pass


class PrintFun(BuiltInFunction):
    name = "print"

    def accept(self, visitor, *args):
        visitor.visit_print(self, *args)


class Float(BuiltInFunction):
    name = "float"

    def accept(self, visitor, value):
        visitor.visit_float(self, value)


class Bool(BuiltInFunction):
    name = "bool"

    def accept(self, visitor, value):
        visitor.visit_bool(self, value)


class Str(BuiltInFunction):
    name = "str"

    def accept(self, visitor, value):
        visitor.visit_str(self, value)


class ToUpper(BuiltInFunction):
    name = "toUpper"

    def accept(self, visitor, value):
        visitor.visit_to_upper(self, value)


class ToLower(BuiltInFunction):
    name = "toLower"

    def accept(self, visitor, value):
        visitor.visit_to_lower(self, value)


class Int(BuiltInFunction):
    name = "int"

    def accept(self, visitor, value):
        visitor.visit_int(self, value)


class BuiltInFunctionExecutor(BuiltInFunctionVisitor):
    def __init__(self):
        self.result = None

    def visit_print(self, _, *args):
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

    def visit_int(self, _, value):
        try:
            self.result = int(value)
        except ValueError:
            raise UnexpectedTypeError("int()", position=None)

    def visit_float(self, _, value):
        try:
            self.result = float(value)
        except ValueError:
            raise UnexpectedTypeError("float()", position=None)

    def visit_bool(self, _, value):
        self.result = bool(value)

    def visit_str(self, _, value):
        self.result = str(value)

    def visit_to_upper(self, _, value):
        if isinstance(value, str):
            self.result = value.upper()
        else:
            raise UnexpectedTypeError("toUpper()", position=None)

    def visit_to_lower(self, _, value):
        if isinstance(value, str):
            self.result = value.lower()
        else:
            raise UnexpectedTypeError("toLower()", position=None)
