from abc import ABC, abstractmethod


# class Node:
#     def __init__(self, position):
#         self.position = position
#
#     def __str__(self, level=0):
#         indent = "  " * level
#         result = f"{indent}{self.__class__.__name__}:\n"
#         for key, value in vars(self).items():
#             if isinstance(value, Node):
#                 result += value.__str__(level + 1)
#             else:
#                 result += f"{indent}  {key}: {value}\n"
#         return result
#
#     def __repr__(self):
#         return self.__str__()

class Program:
    def __init__(self, statements):
        self.statements = statements

    def accept(self, visitor):
        visitor.visit_program(self)


class Statement(ABC):
    def __init__(self, position):
        self.position = position

    def accept(self, visitor):
        pass


class FunctionDefinition(Statement):
    def __init__(self, name, parameters, block, position):
        super().__init__(position)
        self.name = name
        self.parameters = parameters
        self.block = block

    def accept(self, visitor):
        visitor.visit_function_definition(self)


class Block(Statement):
    def __init__(self, statements):
        super().__init__(None)
        self.statements = statements

    def accept(self, visitor):
        visitor.visit_block(self)


class VariableDeclaration(Statement):
    def __init__(self, name, value_expr, position):
        super().__init__(position)
        self.name = name
        self.value_expr = value_expr

    def accept(self, visitor):
        visitor.visit_variable_declaration(self)


class FunctionCall(Statement):
    def __init__(self, name, args, position, parent):
        super().__init__(position)
        self.name = name
        self.args = args
        self.parent = parent

    def accept(self, visitor):
        visitor.visit_function_call(self)


class Assignment(Statement):
    def __init__(self, name, value_expr, position):
        super().__init__(position)
        self.name = name
        self.value_expr = value_expr

    def accept(self, visitor):
        visitor.visit_assignment(self)


class Identifier(Statement):
    def __init__(self, name, position, parent):
        super().__init__(position)
        self.name = name
        self.parent = parent

    def accept(self, visitor):
        visitor.visit_identifier(self)


class BinaryOperation(Statement):
    def __init__(self, operator, left, right, position):
        super().__init__(position)
        self.operator = operator
        self.left = left
        self.right = right

    def accept(self, visitor):
        visitor.visit_binary_operation(self)


class UnaryOperation(Statement):
    def __init__(self, operator, right, position):
        super().__init__(position)
        self.operator = operator
        self.right = right

    def accept(self, visitor):
        visitor.visit_unary_operation(self)


class Literal(Statement):
    def __init__(self, value, position):
        super().__init__(position)
        self.value = value


class IntLiteral(Literal):
    def __init__(self, value, position):
        super().__init__(value, position)

    def accept(self, visitor):
        visitor.visit_int_literal(self)


class FloatLiteral(Literal):
    def __init__(self, value, position):
        super().__init__(value, position)

    def accept(self, visitor):
        visitor.visit_float_literal(self)


class BoolLiteral(Literal):
    def __init__(self, value, position):
        super().__init__(value, position)

    def accept(self, visitor):
        visitor.visit_bool_literal(self)


class StringLiteral(Literal):
    def __init__(self, value, position):
        super().__init__(value, position)

    def accept(self, visitor):
        visitor.visit_string_literal(self)


class NullLiteral(Literal):
    def __init__(self, value, position):
        super().__init__(value, position)

    def accept(self, visitor):
        visitor.visit_null_literal(self)


class ReturnStatement(Statement):
    def __init__(self, value_expr, position):
        super().__init__(position)
        self.value_expr = value_expr

    def accept(self, visitor):
        visitor.visit_return_statement(self)


class IfStatement(Statement):
    def __init__(self, condition, block, position):
        super().__init__(position)
        self.condition = condition
        self.block = block

    def accept(self, visitor):
        visitor.visit_if_statement(self)


class WhileStatement(Statement):
    def __init__(self, condition, block, position):
        super().__init__(position)
        self.condition = condition
        self.block = block

    def accept(self, visitor):
        visitor.visit_while_statement(self)


class ForeachStatement(Statement):
    def __init__(self, variable, iterable, block, position):
        super().__init__(position)
        self.variable = variable
        self.iterable = iterable
        self.block = block

    def accept(self, visitor):
        visitor.visit_foreach_statement(self)


class Visitor(ABC):
    @abstractmethod
    def visit_program(self, program):
        pass

    @abstractmethod
    def visit_block(self, block):
        pass

    @abstractmethod
    def visit_function_definition(self, node):
        pass

    @abstractmethod
    def visit_variable_declaration(self, node):
        pass

    @abstractmethod
    def visit_assignment(self, node):
        pass

    @abstractmethod
    def visit_function_call(self, node):
        pass

    @abstractmethod
    def visit_if_statement(self, node):
        pass

    @abstractmethod
    def visit_while_statement(self, node):
        pass

    @abstractmethod
    def visit_foreach_statement(self, node):
        pass

    @abstractmethod
    def visit_return_statement(self, node):
        pass

    @abstractmethod
    def visit_binary_operation(self, node):
        pass

    @abstractmethod
    def visit_unary_operation(self, node):
        pass

    @abstractmethod
    def visit_identifier(self, node):
        pass

    @abstractmethod
    def visit_int_literal(self, node):
        pass

    @abstractmethod
    def visit_float_literal(self, node):
        pass

    @abstractmethod
    def visit_bool_literal(self, node):
        pass

    @abstractmethod
    def visit_string_literal(self, node):
        pass

    @abstractmethod
    def visit_null_literal(self, node):
        pass

    @abstractmethod
    def visit_print(self, fun, args):
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
