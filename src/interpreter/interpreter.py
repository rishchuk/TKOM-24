from io import StringIO

from src.errors.interpreter_errors import InterpreterError
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

    @staticmethod
    def builtin_print(*args):
        print(*args)

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
        #return interpreter.interpret()

    def visit_IfStatement(self, statement):
        condition = self.visit(statement.condition)
        if condition:
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
        #return self.visit(node.value_expr)

    def visit_BinaryOperation(self, expr):
        left = self.visit(expr.left)
        right = self.visit(expr.right)
        if expr.operator == Operators.ADD_OPERATOR:
            return left + right
        elif expr.operator == Operators.MINUS_OPERATOR:
            return left - right
        elif expr.operator == Operators.MULT_OPERATOR:
            return left * right
        elif expr.operator == Operators.DIV_OPERATOR:
            return left / right
        elif expr.operator == Operators.EQUALS:
            return left == right
        elif expr.operator == Operators.NOT_EQUALS:
            return left != right
        elif expr.operator == Operators.LESS:
            return left < right
        elif expr.operator == Operators.GREATER:
            return left > right
        elif expr.operator == Operators.LESS_THAN_OR_EQUAL:
            return left <= right
        elif expr.operator == Operators.GREATER_THAN_OR_EQUAL:
            return left >= right
        elif expr.operator == Operators.AND_OPERATOR:
            return left and right
        elif expr.operator == Operators.OR_OPERATOR:
            return left or right

    def visit_Identifier(self, identifier):
        return self.env.get_variable(identifier.name)

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
