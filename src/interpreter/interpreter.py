from io import StringIO

from errors.parser_errors import ParserError
from lexer.lexer import CharacterReader, Lexer
from parser.models import FunctionDefinition, ReturnStatement, Visitor
from errors.interpreter_errors import DivisionByZeroError, TypeBinaryError, TypeUnaryError, \
    UnexpectedTypeError, UndefinedVarError, UnexpectedMethodError, UnexpectedAttributeError, InterpreterError, \
    InvalidArgsCountError
from interpreter.environment import Environment
from parser.parser import Operators, Parser


class Interpreter(Visitor):
    def __init__(self, program):
        self.program = program
        self.env = Environment()
        self.setup_builtins()
        self.return_encountered = True
        self.return_value = None

    def setup_builtins(self):
        self.env.set_function('print', self.builtin_print)
        self.env.set_function('int', self.builtin_int)
        self.env.set_function('float', self.builtin_float)
        self.env.set_function('bool', self.builtin_bool)
        self.env.set_function('str', self.builtin_str)
        self.env.set_function('toUpper', self.builtin_to_upper)
        self.env.set_function('toLower', self.builtin_to_lower)

    @staticmethod
    def builtin_to_upper(value):
        if isinstance(value, str):
            return value.upper()
        raise UnexpectedTypeError("toUpper()", position=None)

    @staticmethod
    def builtin_to_lower(value):
        if isinstance(value, str):
            return value.lower()
        raise UnexpectedTypeError("toLower()", position=None)

    def builtin_print(self, *args):
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

    @staticmethod
    def builtin_int(value):
        if isinstance(value, (int, float, str)):
            try:
                return int(value)
            except ValueError:
                raise UnexpectedTypeError("int()", position=None)
        raise UnexpectedTypeError("int()", position=None)

    @staticmethod
    def builtin_float(value):
        if isinstance(value, (int, float, str)):
            try:
                return float(value)
            except ValueError:
                raise UnexpectedTypeError("float()", position=None)
        raise UnexpectedTypeError("float()", position=None)

    @staticmethod
    def builtin_bool(value):
        return bool(value)

    @staticmethod
    def builtin_str(value):
        return str(value)

    def interpret(self):
        return self.program.accept(self)

    def visit_program(self, program):
        for statement in program.statements:
            statement.accept(self)

    def visit_block(self, block):
        self.execute_block(block, Environment(self.env))

    def execute_block(self, block, env):
        prev_env = self.env
        try:
            self.env = env
            for statement in block.statements:
                statement.accept(self)
        finally:
            self.env = prev_env

    def visit_function_definition(self, func_def):
        self.env.set_function(func_def.name, func_def)

    def visit_variable_declaration(self, var):
        value = var.value_expr.accept(self) if var.value_expr else None
        self.env.declare_variable(var.name, value)

    def visit_assignment(self, expr):
        value = expr.value_expr.accept(self)
        self.env.set_variable(expr.name, value)

    def visit_function_call(self, func_call):
        func = self.env.get_function(func_call.name)
        if func_call.parent:
            val = func_call.parent.accept(self)
            if val and func_call.name == 'toLower':
                return self.builtin_to_lower(val)

            if val and func_call.name == 'toUpper':
                return self.builtin_to_upper(val)
            raise UnexpectedMethodError(func_call.name, func_call.position)

        args = [arg.accept(self) for arg in func_call.args]
        if isinstance(func, FunctionDefinition):
            return self.execute_function_call(func, args)
        elif callable(func):
            return func(*args)  # z get fun
        else:
            raise InterpreterError(f"Invalid function call: {func_call.name}", func_call.position)

    def execute_function_call(self, func_def, args):
        if len(func_def.parameters) != len(args):
            raise InvalidArgsCountError(func_def.name, func_def.position)
        env = Environment(parent=self.env)
        for param, arg in zip(func_def.parameters, args):
            env.declare_variable(param.name, arg)
        self.return_encountered = False
        self.return_value = None
        try:
            self.execute_block(func_def.block, env)
        finally:
            if self.return_encountered:
                return self.return_value
        # finally:
        #     self.env = prev_env

    def visit_if_statement(self, statement):
        if statement.condition.accept(self):
            statement.block.accept(self)

    def visit_while_statement(self, statement):
        while statement.condition.accept(self):
            if self.return_encountered:
                break
            statement.block.accept(self)

    def visit_foreach_statement(self, statement):
        iterable = statement.iterable.accept(self)
        if isinstance(iterable, str):
            for item in iterable:
                if self.env.get_variable(statement.variable):
                    self.env.set_variable(statement.variable, item)
                else:
                    self.env.declare_variable(statement.variable, item)
                statement.block.accept(self)
        else:
            raise UnexpectedTypeError(statement.variable, statement.iterable.position)

    def visit_return_statement(self, statement):
        self.return_encountered = True
        self.return_value = statement.value_expr.accept(self) if statement.value_expr else None

    # def visit_ReturnStatement(self, statement):
    #     # self.return_value = self.visit(statement.value_expr)
    #     self.visit(statement.value_expr)

    def visit_binary_operation(self, expr):
        match expr.operator:
            case Operators.ADD_OPERATOR:
                return self.binary_plus(expr.left, expr.right)
            case Operators.MINUS_OPERATOR:
                return self.binary_minus(expr.left, expr.right)
            case Operators.MULT_OPERATOR:
                return self.binary_mult(expr.left, expr.right)
            case Operators.DIV_OPERATOR:
                return self.binary_div(expr.left, expr.right)
            case (Operators.EQUALS | Operators.NOT_EQUALS | Operators.LESS
                  | Operators.GREATER | Operators.LESS_THAN_OR_EQUAL
                  | Operators.GREATER_THAN_OR_EQUAL):
                return self.comparison(expr.operator, expr.left, expr.right)
            case Operators.AND_OPERATOR:
                return self.logical_and(expr.left, expr.right)
            case Operators.OR_OPERATOR:
                return self.logical_or(expr.left, expr.right)

    def binary_plus(self, left_expr, right_expr):
        left = left_expr.accept(self)
        right = right_expr.accept(self)

        if isinstance(left, str) or isinstance(right, str):
            return str(left) + str(right)
        else:
            return left + right

    def binary_minus(self, left_expr, right_expr):
        left = left_expr.accept(self)
        right = right_expr.accept(self)

        if isinstance(left, str) or isinstance(right, str):
            raise TypeBinaryError(left_expr.position)

        return left - right

    def binary_mult(self, left_expr, right_expr):
        left = left_expr.accept(self)
        right = right_expr.accept(self)
        if isinstance(left, str) and isinstance(right, int):
            return left * right
        if isinstance(right, str) and isinstance(left, int):
            return right * left
        if isinstance(left, str) or isinstance(right, str):
            raise TypeBinaryError(left_expr.position)
        return left * right

    def binary_div(self, left_expr, right_expr):
        left = left_expr.accept(self)
        right = right_expr.accept(self)

        if right == 0:
            raise DivisionByZeroError(left_expr.position)
        if isinstance(left, str) or isinstance(right, str):
            raise TypeBinaryError(left_expr.position)

        return left / right

    def comparison(self, operator, left_expr, right_expr):
        left = left_expr.accept(self)
        right = right_expr.accept(self)

        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            pass
        elif isinstance(left, str) and isinstance(right, str):
            if operator == Operators.EQUALS:
                return left == right
            elif operator == Operators.NOT_EQUALS:
                return left != right
            raise TypeBinaryError(left_expr.position)
        else:
            raise TypeBinaryError(left_expr.position)

        match operator:
            case Operators.EQUALS:
                return left == right
            case Operators.NOT_EQUALS:
                return left != right
            case Operators.LESS:
                return left < right
            case Operators.GREATER:
                return left > right
            case Operators.LESS_THAN_OR_EQUAL:
                return left <= right
            case Operators.GREATER_THAN_OR_EQUAL:
                return left >= right

    def visit_unary_operation(self, expr):
        right = expr.right.accept(self)

        match expr.operator:
            case Operators.NEG:
                return not right
            case Operators.MINUS_OPERATOR:
                if isinstance(right, (int, float)):
                    return -right
                raise TypeUnaryError(expr.position)

    def logical_and(self, left_expr, right_expr):  # lenivie
        left = left_expr.accept(self)
        if not left:
            return left

        return right_expr.accept(self)

    def logical_or(self, left_expr, right_expr):
        left = left_expr.accept(self)
        if left:
            return left
        return right_expr.accept(self)

    # def visit_Identifier(self, identifier):
    #     return self.env.get_variable(identifier.name)
    def visit_identifier(self, identifier):
        if identifier.parent:
            val = identifier.parent.accept(self)
            if identifier.name == 'length' and isinstance(val, str):
                val = len(val)
                return val
            else:
                raise UnexpectedAttributeError(identifier.name, identifier.position)
        if self.env.get_variable(identifier.name) is not None:
            return self.env.get_variable(identifier.name)
        raise UndefinedVarError(identifier.name, identifier.position)
    # except UndefinedVarError:
    #
    #     raise UndefinedVarError(identifier.name, identifier.position)

    # nic nie zwraca
    def visit_int_literal(self, int_literal):
        return int_literal.value

    def visit_float_literal(self, float_literal):
        return float_literal.value

    def visit_bool_literal(self, bool_literal):
        return bool_literal.value

    def visit_string_literal(self, string_literal):
        return string_literal.value

    def visit_null_literal(self, null_literal):
        return null_literal.value


# if __name__ == "__main__":
#     code = """
#     print("xxx".toUpper())
#
#     value x = 6
#
#     function add(a, b) {
#         return a * b
#     }
#
#     if x > 5 || x == 4 {
#         print(x)
#     }
#
#     while x > 2 {
#         x = x - 1
#     }
#
#     foreach char in "word" {
#         print(char)
#     }
#
#     value y = 2
#     value result = add(x, y)
#     print("result = ", result)
#     """
#     try:
#         reader = CharacterReader(StringIO(code))
#         lexer = Lexer(reader)
#         parser = Parser(lexer)
#         program = parser.parse_program()
#
#         interpreter = Interpreter(program)
#         interpreter.interpret()
#
#     except ParserError as e:
#         print(e)
#     except InterpreterError as e:
#         print(e)
