from lexer.lexer import *
from enum import Enum, auto

from errors.parser_errors import ExpectedFunctionNameError, ParserError, ExpectedLeftParentAfterFun, \
    ExpectedRightParentAfterFun, \
    ExpectedBlockError, ExpectedParameterAfterCommaError, ExpectedRightBraceError, ExpectedLoopVariableError, \
    ExpectedExpressionError, ExpectedInError, ExpectedConditionError, ExpectedVariableNameError, \
    ExpectedAssignmentOrFunctionCall, ExpectedRightParentAfterFunCall, ExpectedArgumentAfterCommaError, \
    ExpectedRightParentAfterExpression, ExpectedIdentifierAfterDotError, UnexpectedTokenError


class Operators(Enum):
    OR_OPERATOR = auto()
    AND_OPERATOR = auto()
    EQUALS = auto()
    NOT_EQUALS = auto()
    LESS = auto()
    GREATER = auto()
    LESS_THAN_OR_EQUAL = auto()
    GREATER_THAN_OR_EQUAL = auto()
    ADD_OPERATOR = auto()
    MINUS_OPERATOR = auto()
    MULT_OPERATOR = auto()
    DIV_OPERATOR = auto()
    NEG = auto()


OPERATORS = {
    TokenType.OR_OPERATOR: Operators.OR_OPERATOR,
    TokenType.AND_OPERATOR: Operators.AND_OPERATOR,
    TokenType.EQUALS: Operators.EQUALS,
    TokenType.NOT_EQUALS: Operators.NOT_EQUALS,
    TokenType.LESS: Operators.LESS,
    TokenType.GREATER: Operators.GREATER,
    TokenType.LESS_THAN_OR_EQUAL: Operators.LESS_THAN_OR_EQUAL,
    TokenType.GREATER_THAN_OR_EQUAL: Operators.GREATER_THAN_OR_EQUAL,
    TokenType.ADD_OPERATOR: Operators.ADD_OPERATOR,
    TokenType.MINUS_OPERATOR: Operators.MINUS_OPERATOR,
    TokenType.MULT_OPERATOR: Operators.MULT_OPERATOR,
    TokenType.DIV_OPERATOR: Operators.DIV_OPERATOR,
    TokenType.NEG: Operators.NEG,
}


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
    def __init__(self, statemens):
        super().__init__(None)
        self.statemens = statemens


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
    def __init__(self, value, data_type, position):
        super().__init__(position)
        self.value = value
        self.data_type = data_type


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


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.token = self.lexer.get_next_token()

    def maybe(self, expected_type):
        if self.token.type != expected_type:
            return None
        value = self.token
        self.advance()
        return value

    def must_be_(self, expected_type, error):
        if self.token.type != expected_type:
            raise error
        value = self.token
        self.advance()
        return value

    def parse_program(self):
        statements = []
        while statement := self.parse_statement():
            statements.append(statement)

        self.must_be_(TokenType.ETX, UnexpectedTokenError(self.token.position))
        return Program(statements)

    def parse_block_statement(self):
        # var_declaration | if | while | foreach |
        # identifier_or_call, [ "=" , expression ] | return ;
        return (
                self.parse_variable_declaration() or self.parse_if_statement()
                or self.parse_while_statement() or self.parse_foreach_statement()
                or self.parse_return_statement() or self.parse_assignment_or_function_call()
        )

    def parse_statement(self):
        # function_definition | var_declaration | if | while | foreach |
        # identifier_or_call, [ "=" , expression ] | return ;
        return (
                self.parse_function_definition() or self.parse_variable_declaration() or
                self.parse_if_statement() or self.parse_while_statement() or
                self.parse_foreach_statement() or self.parse_return_statement() or
                self.parse_assignment_or_function_call()
        )

    def parse_function_definition(self):
        # function_definition = "function" , identifier , "(" , parameters , ")" , block ;
        position = self.token.position
        if not self.maybe(TokenType.FUNCTION):
            return None

        token = self.must_be_(TokenType.IDENTIFIER, ExpectedFunctionNameError(self.token.position))
        self.must_be_(TokenType.LEFT_PARENT, ExpectedLeftParentAfterFun(self.token.position))
        parameters = self.parse_parameters()
        self.must_be_(TokenType.RIGHT_PARENT, ExpectedRightParentAfterFun(self.token.position))
        position = self.token.position
        if block := self.parse_block():
            return FunctionDefinition(token.value, parameters, block, position)
        raise ExpectedBlockError(position)

    def parse_parameters(self):
        # parameters = [ identifier , { "," , identifier } ]
        params = []

        if not (param := self.parse_parameter()):
            return params
        params.append(param)
        while self.maybe(TokenType.COMMA):
            if not (param := self.parse_parameter()):
                raise ExpectedParameterAfterCommaError(self.token.position)
            params.append(param)
        return params

    def parse_parameter(self):
        position = self.token.position
        if param := self.maybe(TokenType.IDENTIFIER):
            return Identifier(param.value, position, None)
        return None

    def parse_block(self):
        # block = "{", {statement}, "}";
        position = self.token.position
        if not self.maybe(TokenType.LEFT_BRACE):
            return None
        statements = []
        while statement := self.parse_block_statement():
            statements.append(statement)
        self.must_be_(TokenType.RIGHT_BRACE, ExpectedRightBraceError(self.token.position))
        return Block(statements)

    def parse_foreach_statement(self):
        # foreach = "foreach", identifier, "in", expression, block;
        position = self.token.position
        if not self.maybe(TokenType.FOREACH):
            return None
        loop_variable = self.must_be_(TokenType.IDENTIFIER, ExpectedLoopVariableError(self.token.position))
        self.must_be_(TokenType.IN, ExpectedInError(self.token.position))
        if not (iterable_expr := self.parse_expression()):  # ??? expression
            raise ExpectedExpressionError(self.token.position)

        if block := self.parse_block():
            return ForeachStatement(loop_variable, iterable_expr, block, position)
        raise ExpectedBlockError(position)

    def parse_return_statement(self):
        # return = "return", [ expression ];
        position = self.token.position
        if not self.maybe(TokenType.RETURN):
            return None
        value_expr = self.parse_expression()
        return ReturnStatement(value_expr, position)

    def parse_if_statement(self):
        # if = "if" , expression , block  ;
        position = self.token.position
        if not self.maybe(TokenType.IF):
            return None
        if not (condition := self.parse_expression()):
            raise ExpectedConditionError(self.token.position)
        if block := self.parse_block():
            return IfStatement(condition, block, position)
        raise ExpectedBlockError(position)

    def parse_while_statement(self):
        # while = "while" , expression ,  block ;
        position = self.token.position
        if not self.maybe(TokenType.WHILE):
            return None
        if not (condition := self.parse_expression()):
            raise ExpectedConditionError(self.token.position)
        if block := self.parse_block():
            return WhileStatement(condition, block, position)
        raise ExpectedBlockError(position)

    def parse_variable_declaration(self):
        # var_declaration = "value" , identifier , [ "=" , expression ] ;
        position = self.token.position

        if not self.maybe(TokenType.VALUE):
            return None

        token = self.must_be_(TokenType.IDENTIFIER, ExpectedVariableNameError(self.token.position))
        if self.maybe(TokenType.EQUAL):
            if not (value_expr := self.parse_expression()):

                raise SyntaxError(f'Expected expression in variable at {self.token.position}')
        else:
            value_expr = None
        return VariableDeclaration(token.value, value_expr, position)

    def parse_assignment_or_function_call(self):
        # identifier_or_call = identifier , ["(", args , ")"] ;
        position = self.token.position
        if not (token := self.maybe(TokenType.IDENTIFIER)):
            return None
        if fun_call := self.parse_function_call(token.value, position, None):
            return fun_call
        if assignment := self.parse_assignment(token.value):
            return assignment

        raise ExpectedAssignmentOrFunctionCall(self.token.position)

    def parse_function_call(self, name, position, parent):
        # function_call = identifier , "(" , args , ")"
        if not self.maybe(TokenType.LEFT_PARENT):
            return None
        args = self.parse_arguments()
        self.must_be_(TokenType.RIGHT_PARENT, ExpectedRightParentAfterFunCall(self.token.position))

        return FunctionCall(name, args, position, parent)

    def parse_arguments(self):
        # args =  [ expression , { "," , expression } ] ;
        args = []

        if not (arg := self.parse_expression()):
            return args
        args.append(arg)
        while self.maybe(TokenType.COMMA):
            if not (arg := self.parse_expression()):
                raise ExpectedArgumentAfterCommaError(self.token.position)
            args.append(arg)
        return args

    def parse_assignment(self, expression_identifier):
        # assignment = identifier , "=" , expression ;
        position = self.token.position
        if not self.maybe(TokenType.EQUAL):
            return None
        if value_expr := self.parse_expression():
            return Assignment(expression_identifier, value_expr, position)
        raise ExpectedExpressionError(self.token.position)

    def parse_expression(self):
        return self.parse_logical_or()

    def parse_logical_or(self):
        # expression = conjuction, { logical_or , conjuction } ;
        # position = self.token.position
        if not (left_expr := self.parse_logical_and()):
            return None
        position = self.token.position
        while operator := self.maybe(TokenType.OR_OPERATOR):
            # operator = self.token.value

            if not (right_expr := self.parse_logical_and()):
                raise ExpectedExpressionError(self.token.position)

            left_expr = BinaryOperation(OPERATORS[operator.type], left_expr, right_expr, position)  # enumerator zamiast operator

        return left_expr

    def parse_logical_and(self):
        #  conjuction = equality, { logical_and , equality} ;
        if not (left_expr := self.parse_equality()):
            return None
        position = self.token.position
        while operator := self.maybe(TokenType.AND_OPERATOR):
            if not (right_expr := self.parse_equality()):
                raise ExpectedExpressionError(self.token.position)
            left_expr = BinaryOperation(OPERATORS[operator.type], left_expr, right_expr, position)

        return left_expr

    def parse_equality(self):
        if not (left_expr := self.parse_relational()):
            return None
        position = self.token.position
        if operator := self.maybe(TokenType.EQUALS) or self.maybe(TokenType.NOT_EQUALS):

            if not (right_expr := self.parse_relational()):
                raise ExpectedExpressionError(self.token.position)
            left_expr = BinaryOperation(OPERATORS[operator.type], left_expr, right_expr, position)

        return left_expr

    def parse_relational(self):
        if not (left_expr := self.parse_additive()):
            return None
        position = self.token.position
        while operator := self.maybe(TokenType.LESS) or \
                          self.maybe(TokenType.GREATER) or \
                          self.maybe(TokenType.LESS_THAN_OR_EQUAL) or \
                          self.maybe(TokenType.GREATER_THAN_OR_EQUAL):

            if not (right_expr := self.parse_additive()):
                raise ExpectedExpressionError(self.token.position)
            left_expr = BinaryOperation(OPERATORS[operator.type], left_expr, right_expr, position)

        return left_expr

    def parse_additive(self):
        # additive_expression = term , { add_sub_operator , term } ;
        if not (left_expr := self.parse_multiplicative()):
            return None
        position = self.token.position
        while operator := self.maybe(TokenType.ADD_OPERATOR) or \
                          self.maybe(TokenType.MINUS_OPERATOR):

            if not (right_expr := self.parse_multiplicative()):
                raise ExpectedExpressionError(self.token.position)
            left_expr = BinaryOperation(OPERATORS[operator.type], left_expr, right_expr, position)

        return left_expr

    def parse_multiplicative(self):
        # term = factor , { mul_div_operator , factor } ;
        if not (left_expr := self.parse_unary()):
            return None
        position = self.token.position
        while operator := self.maybe(TokenType.MULT_OPERATOR) or \
                          self.maybe(TokenType.DIV_OPERATOR):
            if not (right_expr := self.parse_unary()):
                raise ExpectedExpressionError(self.token.position)
            left_expr = BinaryOperation(OPERATORS[operator.type], left_expr, right_expr, position)

        return left_expr

    def parse_unary(self):
        # factor = ["!" | "-"], (number | string | bool | attr_method | "(", expression, ")");
        position = self.token.position
        if operator := self.maybe(TokenType.MINUS_OPERATOR) or \
                       self.maybe(TokenType.NEG):
            right = self.parse_primary()
            if not right:
                raise ExpectedExpressionError(self.token.position)

            return UnaryOperation(OPERATORS[operator.type], right, position)
        return self.parse_primary()

    def parse_primary(self):
        return (
            self.parse_identifier_or_fun_call() or self.parse_literal() or self.parse_parenthesized_expression()
        )

    def parse_dot_chain(self, parent):
        position = self.token.position
        while self.maybe(TokenType.DOT):
            token = self.must_be_(TokenType.IDENTIFIER, ExpectedIdentifierAfterDotError(self.token.position))
            if not (item := self.parse_function_call(token.value, position, parent)):
                item = Identifier(token.value, position, parent)
            parent = item
        return parent

    def parse_identifier_or_fun_call(self):
        position = self.token.position
        if not (token := self.maybe(TokenType.IDENTIFIER)):
            return None

        if not (item := self.parse_function_call(token.value, position, None)):
            item = Identifier(token.value, position, None)

        # while self.maybe(TokenType.DOT):
        #     token = self.must_be_(TokenType.IDENTIFIER, f'Expected identifier or function call after "." {self.token.position}')
        #     if not (item := self.parse_function_call(token.value, position, item)):
        #         item = Identifier(token.value, position, item)

        return self.parse_dot_chain(item)
    # a.b.c
    # c -> b -> a

    def parse_literal(self):  # int_literal, bool_literal ...
        value = self.token.value
        position = self.token.position

        if self.maybe(TokenType.INT_CONST):
            return Literal(value, TokenType.INT_CONST, position)
        if self.maybe(TokenType.FLOAT_CONST):
            return Literal(value, TokenType.FLOAT_CONST, position)
        if self.maybe(TokenType.TRUE_CONST):
            return Literal(value, TokenType.TRUE_CONST, position)
        if self.maybe(TokenType.FALSE_CONST):
            return Literal(value, TokenType.FALSE_CONST, position)
        if self.maybe(TokenType.STRING):
            literal = Literal(value, TokenType.STRING, position)
            return self.parse_dot_chain(literal)
        return None

    def parse_parenthesized_expression(self):
        position = self.token.position
        if not self.maybe(TokenType.LEFT_PARENT):
            return None
        if not (expression := self.parse_expression()):
            raise ExpectedExpressionError(self.token.position)
        self.must_be_(TokenType.RIGHT_PARENT, ExpectedRightParentAfterExpression(self.token.position))
        return expression

    def advance(self):
        self.token = self.lexer.get_next_token()


if __name__ == "__main__":
    code = """ 
    function add(a, b) {
        return 42
    }
    
    if !(x > 5) || x == 4 {
        print(x)
    }
    
    while x > 1 {
        x = x + 1
    }
    
    foreach char in word {
        print(char)
    }
    
    value result = add(x, y)
    print(result)

    """

    file_name = "..\input.xd"

    try:
        # with open(file_name, 'r') as file:
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser = Parser(lexer)
        program = parser.parse_program()

        print(program)

    except ParserError as e:
        print(e)

