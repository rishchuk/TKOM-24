from io import StringIO

from src.errors.interpreter_errors import InterpreterError, DivisionByZeroError, TypeBinaryError, TypeUnaryError, \
    UnexpectedTypeError, UndefinedVarError, UnexpectedMethodError, UnexpectedAttributeError
from src.errors.parser_errors import ParserError
from src.interpreter.environment import Environment
from src.interpreter.visitor import Visitor
from src.lexer.lexer import CharacterReader, Lexer
from src.parser.parser import Parser, Operators


class Interpreter(Visitor):
    def __init__(self, program):
        self.program = program
        self.env = Environment()
        self.return_value = None
        self.setup_builtins()

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
        raise UnexpectedTypeError("toUpper()")

    @staticmethod
    def builtin_to_lower(value):
        if isinstance(value, str):
            return value.lower()
        raise UnexpectedTypeError("toLower()")

    @staticmethod
    def builtin_print(*args):
        print(*args)

    @staticmethod
    def builtin_int(value):
        if isinstance(value, (int, float, str)):
            try:
                return int(value)
            except ValueError:
                raise UnexpectedTypeError("int()")
        raise UnexpectedTypeError("int()")

    @staticmethod
    def builtin_float(value):
        if isinstance(value, (int, float, str)):
            try:
                return float(value)
            except ValueError:
                raise UnexpectedTypeError("float()")
        raise UnexpectedTypeError("float()")

    @staticmethod
    def builtin_bool(value):
        return bool(value)

    @staticmethod
    def builtin_str(value):
        return str(value)

    def interpret(self):
        return self.visit(self.program)

    def visit_Program(self, program):
        for statement in program.statements:
            self.visit(statement)

    def visit_Block(self, block):
        for statement in block.statements:
            self.visit(statement)

    def visit_FunctionDefinition(self, func_def):
        self.env.set_function(func_def.name, func_def)

    def visit_VariableDeclaration(self, var):
        value = self.visit(var.value_expr) if var.value_expr else None
        self.env.declare_variable(var.name, value)

    def visit_Assignment(self, expr):
        value = self.visit(expr.value_expr)
        self.env.set_variable(expr.name, value)

    def visit_FunctionCall(self, func_call):
        func = self.env.get_function(func_call.name)
        if func_call.parent:
            val = self.visit(func_call.parent)
            if val and func_call.name == 'toLower':
                return self.builtin_to_lower(val)

            if val and func_call.name == 'toUpper':
                return self.builtin_to_upper(val)
            raise UnexpectedMethodError(func_call.name)

        args = [self.visit(arg) for arg in func_call.args]
        if callable(func):
            return func(*args)
        return self.execute_function(func, args)

    def execute_function(self, func, args):
        context = Environment(parent=self.env)
        for param, arg in zip(func.parameters, args):
            context.set_variable(param.name, arg)
        interpreter = Interpreter(func.block)
        interpreter.env = context
        result = interpreter.interpret()
        return interpreter.return_value
        # return interpreter.interpret()

    def visit_IfStatement(self, statement):
        if self.visit(statement.condition):
            self.visit(statement.block)

    def visit_WhileStatement(self, statement):
        while self.visit(statement.condition):
            self.visit(statement.block)

    def visit_ForeachStatement(self, statement):
        iterable = self.visit(statement.iterable)
        for item in iterable:
            self.env.set_variable(statement.variable, item)
            self.visit(statement.block)

    def visit_ReturnStatement(self, statement):
        self.return_value = self.visit(statement.value_expr)
        # return self.visit(statement.value_expr)

    def visit_BinaryOperation(self, expr):
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
        left = self.visit(left_expr)
        right = self.visit(right_expr)

        if isinstance(left, str) or isinstance(right, str):
            return str(left) + str(right)
        else:
            return left + right

    def binary_minus(self, left_expr, right_expr):
        left = self.visit(left_expr)
        right = self.visit(right_expr)

        if isinstance(left, str) or isinstance(right, str):
            raise TypeBinaryError()

        return left - right

    def binary_mult(self, left_expr, right_expr):
        left = self.visit(left_expr)
        right = self.visit(right_expr)
        if isinstance(left, str) and isinstance(right, int):
            return left * right
        if isinstance(right, str) and isinstance(left, int):
            return right * left
        if isinstance(left, str) or isinstance(right, str):
            raise TypeBinaryError()
        return left * right

    def binary_div(self, left_expr, right_expr):
        left = self.visit(left_expr)
        right = self.visit(right_expr)

        if right == 0:
            raise DivisionByZeroError()
        if isinstance(left, str) or isinstance(right, str):
            raise TypeBinaryError()

        return left / right

    def comparison(self, operator, left_expr, right_expr):
        left = self.visit(left_expr)
        right = self.visit(right_expr)

        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            pass
        elif isinstance(left, str) and isinstance(right, str):
            if operator == Operators.EQUALS:
                return left == right
            elif operator == Operators.NOT_EQUALS:
                return left != right
            raise TypeBinaryError()
        else:
            raise TypeBinaryError()

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

    def visit_UnaryOperation(self, expr):
        right = self.visit(expr.right)

        match expr.operator:
            case Operators.NEG:
                return not right
            case Operators.MINUS_OPERATOR:
                if isinstance(right, (int, float)):
                    return -right
                raise TypeUnaryError()

    def logical_and(self, left_expr, right_expr):
        left = self.visit(left_expr)
        right = self.visit(right_expr)

        return left and right

    def logical_or(self, left_expr, right_expr):
        left = self.visit(left_expr)
        right = self.visit(right_expr)

        return left or right

    # def visit_Identifier(self, identifier):
    #     return self.env.get_variable(identifier.name)
    def visit_Identifier(self, identifier):
        try:
            return self.env.get_variable(identifier.name)
        except UndefinedVarError:
            if identifier.parent:

                if val := self.visit(identifier.parent):
                    if identifier.name == 'length':
                        val = len(val)
                else:
                    raise UnexpectedAttributeError(identifier.name)

                self.env.set_variable(identifier.name, val)
                return self.env.get_variable(identifier.name)
            raise UndefinedVarError(identifier.name)

    @staticmethod
    def visit_IntLiteral(int_literal):
        return int_literal.value

    @staticmethod
    def visit_FloatLiteral(float_literal):
        return float_literal.value

    @staticmethod
    def visit_BoolLiteral(bool_literal):
        return bool_literal.value

    @staticmethod
    def visit_StringLiteral(string_literal):
        return string_literal.value


if __name__ == "__main__":
    code = """ 
    print("xxx".toUpper())
    
    value x = 6
    
    function add(a, b) {
        return a * b
    }
    
    if x > 5 || x == 4 {
        print(x)
    }
    
    while x > 2 {
        x = x - 1
    }
    
    foreach char in "word" {
        print(char)
    }
    
    value y = 2
    value result = add(x, y)
    print("result = ", result)
    """
    try:
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser = Parser(lexer)
        program = parser.parse_program()

        interpreter = Interpreter(program)
        interpreter.interpret()

    except ParserError as e:
        print(e)
    except InterpreterError as e:
        print(e)
