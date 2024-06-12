from io import StringIO

from errors.parser_errors import ParserError
from interpreter.builtin_functions import PrintFun, Int, Float, Bool, Str, ToUpper, ToLower, Statement
from lexer.lexer import CharacterReader, Lexer
from parser.models import FunctionDefinition, ReturnStatement, Visitor
from errors.interpreter_errors import DivisionByZeroError, TypeBinaryError, TypeUnaryError, \
    UnexpectedTypeError, UndefinedVarError, UnexpectedMethodError, UnexpectedAttributeError, InterpreterError, \
    InvalidArgsCountError, RecursionLimitError, UndefinedFunctionError
from interpreter.environment import Environment
from parser.parser import Operators, Parser


class Interpreter(Visitor):
    def __init__(self, program):
        self.program = program
        self.env = Environment()
        self.setup_builtins()
        self.return_encountered = False
        self.max_recursion_depth = 80
        self.recursion_depth = 0
        self.result = None
        self.return_value = None

    def check_recursion_depth(self):
        if self.recursion_depth > self.max_recursion_depth:
            raise RecursionLimitError()

    def setup_builtins(self):
        for fun in (PrintFun, Int, Float, Bool, Str, ToUpper, ToLower):
            self.env.define_builtins_function(fun(None))

    def interpret(self):
        self.program.accept(self)

    def visit_program(self, program):
        function_definitions = []
        statements = []
        for statement in program.statements:
            if isinstance(statement, FunctionDefinition):
                function_definitions.append(statement)
            else:
                statements.append(statement)

        for func_def in function_definitions:
            func_def.accept(self)

        for stmt in statements:
            stmt.accept(self)

    def visit_block(self, block):
        for statement in block.statements:
            statement.accept(self)
            if self.return_encountered:
                break

    def visit_function_definition(self, func_def):
        self.env.set_function(func_def)

    def visit_variable_declaration(self, var):
        if var.value_expr:
            var.value_expr.accept(self)
            value = self.result
        else:
            value = None
        self.env.declare_variable(var.name, value)

    def visit_assignment(self, expr):
        expr.value_expr.accept(self)
        value = self.result
        self.env.set_variable(expr.name, value)

    def visit_function_call(self, func_call):
        func = self.env.get_function(func_call.name)
        self.return_value = None

        if func_call.parent:
            func_call.parent.accept(self)
            val = self.result
            if isinstance(func, (ToUpper, ToLower)):
                func.accept(self, val)
                return

        args = []
        for arg in func_call.args:
            arg.accept(self)
            args.append(self.result)

        if isinstance(func, (PrintFun, Int, Float, Str, Bool)):
            func.accept(self, *args)
        elif isinstance(func, FunctionDefinition):
            self.check_recursion_depth()
            self.recursion_depth += 1
            try:
                if len(args) != len(func.parameters):
                    raise InvalidArgsCountError(func_call.name, func_call.position)

                self.env.new_scope(func.parameters, args)
                func.block.accept(self)
                self.result = self.return_value
                self.env.del_scope()
                self.return_encountered = False
            finally:
                self.recursion_depth -= 1

        else:
            raise UndefinedFunctionError(func_call.name, func_call.position)

    def visit_if_statement(self, statement):
        statement.condition.accept(self)
        if self.result:
            statement.block.accept(self)
            if self.return_encountered:
                return

    def visit_while_statement(self, statement):
        self.recursion_depth = 0
        while True:
            self.check_recursion_depth()
            statement.condition.accept(self)
            if not self.result:
                break
            statement.block.accept(self)
            if self.return_encountered:
                break

            self.recursion_depth += 1

    def visit_foreach_statement(self, statement):
        statement.iterable.accept(self)
        iterable = self.result
        if isinstance(iterable, str):
            for item in iterable:
                if self.env.get_variable(statement.variable):
                    self.env.set_variable(statement.variable, item)
                else:
                    self.env.declare_variable(statement.variable, item)
                statement.block.accept(self)
                if self.return_encountered:
                    return
        else:
            raise UnexpectedTypeError(statement.variable, statement.iterable.position)

    def visit_return_statement(self, statement):
        self.return_encountered = True
        if statement.value_expr:
            statement.value_expr.accept(self)
            self.return_value = self.result
        else:
            self.return_value = None

    def visit_binary_operation(self, expr):
        expr.left.accept(self)
        left = self.result
        expr.right.accept(self)
        right = self.result

        if self.is_boolean(left): left = self.to_bool(left)
        if self.is_boolean(right): right = self.to_bool(right)

        match expr.operator:
            case Operators.ADD_OPERATOR:
                self.result = self.binary_plus(left, right)
            case Operators.MINUS_OPERATOR:
                self.result = self.binary_minus(left, right)
            case Operators.MULT_OPERATOR:
                self.result = self.binary_mult(left, right)
            case Operators.DIV_OPERATOR:
                self.result = self.binary_div(left, right)
            case (Operators.EQUALS | Operators.NOT_EQUALS | Operators.LESS
                  | Operators.GREATER | Operators.LESS_THAN_OR_EQUAL
                  | Operators.GREATER_THAN_OR_EQUAL):
                self.result = self.comparison(expr.operator, left, right)
            case Operators.AND_OPERATOR:
                self.result = self.logical_and(left, right)
            case Operators.OR_OPERATOR:
                self.result = self.logical_or(left, right)

    def binary_plus(self, left, right):
        if isinstance(left, str) or isinstance(right, str):
            return str(left) + str(right)
        else:
            return left + right

    def binary_minus(self, left, right):
        if isinstance(left, str) or isinstance(right, str):
            raise TypeBinaryError(position=None)
        return left - right

    def binary_mult(self, left, right):
        if isinstance(left, str) and isinstance(right, int):
            return left * right
        if isinstance(right, str) and isinstance(left, int):
            return right * left
        if isinstance(left, str) or isinstance(right, str):
            raise TypeBinaryError(position=None)
        return left * right

    def binary_div(self, left, right):
        if right == 0:
            raise DivisionByZeroError(position=None)
        if isinstance(left, str) or isinstance(right, str):
            raise TypeBinaryError(position=None)
        return left / right

    def comparison(self, operator, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            pass
        elif isinstance(left, str) and isinstance(right, str):
            if operator == Operators.EQUALS:
                return left == right
            elif operator == Operators.NOT_EQUALS:
                return left != right
            raise TypeBinaryError(position=None)
        else:
            raise TypeBinaryError(position=None)
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
        expr.right.accept(self)
        right = self.result
        match expr.operator:
            case Operators.NEG:
                if self.is_boolean(right): right = self.to_bool(right)
                self.result = not right
            case Operators.MINUS_OPERATOR:
                if isinstance(right, (int, float)):
                    self.result = -right
                else:
                    raise TypeUnaryError(expr.position)

    def logical_and(self, left, right):
        if not left:
            return left
        return right

    def logical_or(self, left, right):
        if left:
            return left
        return right

    def visit_identifier(self, identifier):
        if identifier.parent:
            identifier.parent.accept(self)
            val = self.result
            if identifier.name == 'length' and isinstance(val, str):
                self.result = len(val)
            else:
                raise UnexpectedAttributeError(identifier.name, identifier.position)
        elif self.env.get_variable(identifier.name):
            self.result = self.env.get_variable(identifier.name)[0]
        else:
            raise UndefinedVarError(identifier.name, identifier.position)

    def visit_int_literal(self, int_literal):
        self.result = int_literal.value

    def visit_float_literal(self, float_literal):
        self.result = float_literal.value

    def visit_bool_literal(self, bool_literal):
        self.result = bool_literal.value

    def visit_string_literal(self, string_literal):
        self.result = string_literal.value

    def visit_null_literal(self, null_literal):
        self.result = null_literal.value

    def visit_print(self, fun, *args):
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

    def visit_int(self, fun, value):
        try:
            self.result = int(value)
        except ValueError:
            raise UnexpectedTypeError("int()", position=None)

    def visit_float(self, fun, value):
        try:
            self.result = float(value)
        except ValueError:
            raise UnexpectedTypeError("float()", position=None)

    def visit_bool(self, fun, value):
        self.result = bool(value)

    def visit_str(self, fun, value):
        self.result = str(value)

    def visit_to_upper(self, fun, value):
        if isinstance(value, str):
            self.result = value.upper()
        else:
            raise UnexpectedTypeError("toUpper()", position=None)

    def visit_to_lower(self, fun, value):
        if isinstance(value, str):
            self.result = value.lower()
        else:
            raise UnexpectedTypeError("toLower()", position=None)

    def is_boolean(self, value):
        return isinstance(value, str) and value in {"true", "false"}

    def to_bool(self, value):
        if value == "true":
            return True
        elif value == "false":
            return False
        raise UnexpectedTypeError(value, None)


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
