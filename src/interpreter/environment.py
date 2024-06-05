from errors.interpreter_errors import DuplicateFunDeclarationError, DuplicateVarDeclarationError, \
    UndefinedVarError


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

    def set_variable(self, name, value):
        if name in self.variables:
            self.variables[name] = value
        elif self.parent:
            self.parent.set_variable(name, value)
        else:
            raise UndefinedVarError(name, position=None)

    def declare_variable(self, name, value):
        if name in self.variables:
            raise DuplicateVarDeclarationError(name, position=None)
        self.variables[name] = value

    def get_function(self, name):
        if name in self.functions:
            return self.functions[name]
        elif self.parent:
            return self.parent.get_function(name)

    def set_function(self, name, func):
        if name in self.functions:
            raise DuplicateFunDeclarationError(name, position=None)
        self.functions[name] = func
