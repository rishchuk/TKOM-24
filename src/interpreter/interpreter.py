from io import StringIO

from errors.parser_errors import ParserError
from interpreter.builtin_functions import PrintFun, Int, Float, Bool, Str, ToUpper, ToLower, BuiltInFunction, \
    BuiltInFunctionExecutor
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
        self.return_value = None
        self.max_recursion_depth = 80
        self.recursion_depth = 0
        self.result = None

    def check_recursion_depth(self):
        if self.recursion_depth > self.max_recursion_depth:
            raise RecursionLimitError()

    def setup_builtins(self):
        for fun in (PrintFun, Int, Float, Bool, Str, ToUpper, ToLower):
            self.env.define_builtins_function(fun())

    def interpret(self):
        return self.program.accept(self)

    def visit_program(self, program):
        # 2 visitator przed 1 statement, separuje od definicji funkcji
        for statement in program.statements:  # deklaracja funcji
            self.check_recursion_depth()
            statement.accept(self)
        # statements, definicje funkcji

    def visit_block(self, block):   # visit_block
        self.execute_block(block, Environment(self.env))

    def execute_block(self, block, env):
        prev_env = self.env
        try:
            self.env = env
            for statement in block.statements:
                self.check_recursion_depth()
                statement.accept(self)
                if self.return_encountered:
                    break
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
            if isinstance(func, (ToUpper, ToLower)):
                executor = BuiltInFunctionExecutor()
                func.accept(executor, val)
                return executor.result
        args = [arg.accept(self) for arg in func_call.args]

        if isinstance(func, (PrintFun, Int, Float, Str, Bool)):
            executor = BuiltInFunctionExecutor()
            func.accept(executor, *args)
            return executor.result
        elif isinstance(func, FunctionDefinition):
            self.check_recursion_depth()
            self.recursion_depth += 1
            try:
                return func.execute(args, self)
            finally:
                self.recursion_depth -= 1
        else:
            raise UndefinedFunctionError(func_call.name, func_call.position)

    # def execute_function_call(self, func_def, args):
    #     self.recursion_depth += 1
    #     try:
    #         if len(func_def.parameters) != len(args):
    #             raise InvalidArgsCountError(func_def.name, func_def.position)
    #         env = Environment(parent=self.env)
    #         for param, arg in zip(func_def.parameters, args):
    #             env.declare_variable(param.name, arg)
    #         prev_return_encountered = self.return_encountered
    #         prev_return_value = self.return_value
    #         self.return_encountered = False
    #         self.return_value = None
    #         func_def.block.accept(self)
    #         return_value = self.return_value
    #         self.return_encountered = prev_return_encountered
    #         self.return_value = prev_return_value
    #         return return_value
    #     finally:
    #         self.recursion_depth -= 1

    def visit_if_statement(self, statement):
        if statement.condition.accept(self):
            statement.block.accept(self)
            if self.return_encountered:
                return

    def visit_while_statement(self, statement):
        while statement.condition.accept(self):
            statement.block.accept(self)
            if self.return_encountered:
                return

    def visit_foreach_statement(self, statement):
        iterable = statement.iterable.accept(self)
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
        self.return_value = statement.value_expr.accept(self) if statement.value_expr else None

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

    def logical_and(self, left_expr, right_expr):
        left = left_expr.accept(self)
        if not left:
            return left
        return right_expr.accept(self)

    def logical_or(self, left_expr, right_expr):
        left = left_expr.accept(self)
        if left:
            return left
        return right_expr.accept(self)

    def visit_identifier(self, identifier):
        if identifier.parent:
            val = identifier.parent.accept(self)
            if identifier.name == 'length' and isinstance(val, str):
                val = len(val)
                return val
            else:
                raise UnexpectedAttributeError(identifier.name, identifier.position)
        if self.env.get_variable(identifier.name):
            return self.env.get_variable(identifier.name)[0]

        raise UndefinedVarError(identifier.name, identifier.position)

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
