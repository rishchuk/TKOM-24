from errors.interpreter_errors import DuplicateFunDeclarationError, DuplicateVarDeclarationError, \
    UndefinedFunctionError, UndefinedVarError


class Environment:
    def __init__(self, parent=None):
        self.variables = {}
        self.functions = {}
        self.parent = parent

    def get_variable(self, name):
        if name in self.variables:
            return self.variables[name]
        elif self.parent:
            return self.parent.get_variable(name)
        raise UndefinedVarError(name)

    def set_variable(self, name, value):
        if self.parent or name in self.variables:
            self.variables[name] = value
        else:
            raise UndefinedVarError(name)

    def declare_variable(self, name, value):
        if name in self.variables:
            raise DuplicateVarDeclarationError(name)
        self.variables[name] = value

    def get_function(self, name):
        if name in self.functions:
            return self.functions[name]
        elif self.parent:
            return self.parent.get_function(name)
        raise UndefinedFunctionError(name)

    def set_function(self, name, func):
        if name in self.functions:
            raise DuplicateFunDeclarationError(name)
        self.functions[name] = func
