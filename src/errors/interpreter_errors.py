
class InterpreterError(Exception):
    def __init__(self, error_message):
        super().__init__(error_message)

    def __str__(self):
        return super().__str__()


class DuplicateFunDeclarationError(InterpreterError):
    def __init__(self, name):
        super().__init__(f"Function '{name}' already declared")


class DuplicateVarDeclarationError(InterpreterError):
    def __init__(self, name):
        super().__init__(f"Variable '{name}' already declared")


class UndefinedFunctionError(InterpreterError):
    def __init__(self, name):
        super().__init__(f"Function '{name}' not defined")


class UndefinedVarError(InterpreterError):
    def __init__(self, name):
        super().__init__(f"Variable '{name}' not defined")
