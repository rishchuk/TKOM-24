from errors.interpreter_errors import DuplicateFunDeclarationError, DuplicateVarDeclarationError, \
    UndefinedVarError


class Scope:
    def __init__(self, parent=None):
        self.parent = parent
        self.variables = {}

    def declare_variable(self, name, value):
        if name in self.variables:
            raise DuplicateVarDeclarationError(name, position=None)
        self.variables[name] = value

    def set_variable(self, name, value):
        if name in self.variables:
            self.variables[name] = value
        else:
            raise UndefinedVarError(name, None)

    def get_variable(self, name):
        if name in self.variables:
            return [self.variables[name]]
        elif self.parent is not None:
            return self.parent.get_variable(name)


class GlobalScope(Scope):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.functions = {}

    def set_function(self, func):
        if func.name in self.functions:
            raise DuplicateFunDeclarationError(func.name, position=None)
        self.functions[func.name] = func

    def get_function(self, name):
        if name in self.functions:
            return self.functions[name]


class Environment:
    def __init__(self):
        self.global_scope = GlobalScope()
        self.current_scope = self.global_scope
        self.stack = []

    def declare_variable(self, name, value):
        self.current_scope.declare_variable(name, value)

    def set_variable(self, name, value):
        self.current_scope.set_variable(name, value)

    def get_variable(self, name):
        return self.current_scope.get_variable(name)

    def set_function(self, func):
        self.global_scope.set_function(func)

    def get_function(self, func):
        return self.global_scope.get_function(func)

    def new_scope(self, parameters, args):
        self.stack.append(self.current_scope)
        self.current_scope = Scope(self.global_scope)
        for param, arg in zip(parameters, args):
            self.current_scope.variables[param.name] = arg

    def del_scope(self):
        if self.stack:
            self.current_scope = self.stack.pop()
        else:
            self.current_scope = self.global_scope

    def define_builtins_function(self, function):
        self.global_scope.functions[function.name] = function


