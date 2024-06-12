
class InterpreterError(Exception):
    def __init__(self, error_message, position):
        super().__init__(error_message)
        self.position = position

    def __str__(self):
        if self.position:
            return f'{super().__str__()}: {self.position}'
        return f'{super().__str__()}'


class DuplicateFunDeclarationError(InterpreterError):
    def __init__(self, name, position):
        super().__init__(f"Function '{name}' already declared", position)


class DuplicateVarDeclarationError(InterpreterError):
    def __init__(self, name, position):
        super().__init__(f"Variable '{name}' already declared", position)


class UndefinedFunctionError(InterpreterError):
    def __init__(self, name, position):
        super().__init__(f"Function '{name}' not defined", position)


class UndefinedVarError(InterpreterError):
    def __init__(self, name, position):
        super().__init__(f"Variable '{name}' not defined", position)
        

class DivisionByZeroError(InterpreterError):
    def __init__(self, position):
        super().__init__(f"Division by zero is not allowed", position)


class TypeBinaryError(InterpreterError):
    def __init__(self, position):
        super().__init__(f"Error between types", position)


class TypeUnaryError(InterpreterError):
    def __init__(self, position):
        super().__init__(f"Error type", position)


class UnexpectedTypeError(InterpreterError):
    def __init__(self, name, position):
        super().__init__(f"Invalid argument type for {name}", position)


class UnexpectedMethodError(InterpreterError):
    def __init__(self, name, position):
        super().__init__(f"Invalid method {name}() on str", position)


class UnexpectedAttributeError(InterpreterError):
    def __init__(self, name, position):
        super().__init__(f"Invalid attribute {name} on str", position)


class InvalidArgsCountError(InterpreterError):
    def __init__(self, name, position):
        super().__init__(f"Invalid count of args for {name}", position)


class RecursionLimitError(InterpreterError):
    def __init__(self, position=None):
        super().__init__("Maximum recursion depth exceeded", position)
