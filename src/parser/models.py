class Node:
    def __init__(self, position):
        self.position = position

    def __str__(self, level=0):
        indent = "  " * level
        result = f"{indent}{self.__class__.__name__}:\n"
        for key, value in vars(self).items():
            if isinstance(value, Node):
                result += value.__str__(level + 1)
            else:
                result += f"{indent}  {key}: {value}\n"
        return result

    def __repr__(self):
        return self.__str__()


class Program(Node):
    def __init__(self, statements):
        super().__init__(None)
        self.statements = statements


class Identifier(Node):
    def __init__(self, name, position, parent):
        super().__init__(position)
        self.name = name
        self.parent = parent


class FunctionDefinition(Node):
    def __init__(self, name, parameters, block, position):
        super().__init__(position)
        self.name = name
        self.parameters = parameters
        self.block = block


class Block(Node):
    def __init__(self, statements):
        super().__init__(None)
        self.statements = statements


class VariableDeclaration(Node):
    def __init__(self, name, value_expr, position):
        super().__init__(position)
        self.name = name
        self.value_expr = value_expr


class FunctionCall(Node):
    def __init__(self, name, args, position, parent):
        super().__init__(position)
        self.name = name
        self.args = args
        self.parent = parent


class Assignment(Node):
    def __init__(self, name, value_expr, position):
        super().__init__(position)
        self.name = name
        self.value_expr = value_expr


class BinaryOperation(Node):
    def __init__(self, operator, left, right, position):
        super().__init__(position)
        self.operator = operator
        self.left = left
        self.right = right


class UnaryOperation(Node):
    def __init__(self, operator, right, position):
        super().__init__(position)
        self.operator = operator
        self.right = right


class Literal(Node):
    def __init__(self, value, position):
        super().__init__(position)
        self.value = value


class IntLiteral(Literal):
    def __init__(self, value, position):
        super().__init__(value, position)


class FloatLiteral(Literal):
    def __init__(self, value, position):
        super().__init__(value, position)


class BoolLiteral(Literal):
    def __init__(self, value, position):
        super().__init__(value, position)


class StringLiteral(Literal):
    def __init__(self, value, position):
        super().__init__(value, position)


class NullLiteral(Literal):
    def __init__(self, value, position):
        super().__init__(value, position)


class ReturnStatement(Node):
    def __init__(self, value_expr, position):
        super().__init__(position)
        self.value_expr = value_expr


class IfStatement(Node):
    def __init__(self, condition, block, position):
        super().__init__(position)
        self.condition = condition
        self.block = block


class WhileStatement(Node):
    def __init__(self, condition, block, position):
        super().__init__(position)
        self.condition = condition
        self.block = block


class ForeachStatement(Node):
    def __init__(self, variable, iterable, block, position):
        super().__init__(position)
        self.variable = variable
        self.iterable = iterable
        self.block = block
