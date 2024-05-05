from lexer.lexer import *


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
    def __init__(self, functions):
        super().__init__(None)
        self.functions = functions


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
    def __init__(self, name, args, position):
        super().__init__(position)
        self.name = name
        self.args = args


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

    def must_be(self, expected_type):
        if self.token.type != expected_type:
            return None
        value = self.token.type
        self.advance()
        return value

    def must_be_(self, expected_type, error_message=None):
        if self.token.type != expected_type:
            raise SyntaxError(error_message)
        value = self.token.type
        self.advance()
        return value

    def parse_program(self):
        statements = []
        while statement := self.parse_statement():
            statements.append(statement)

        return Program(statements)

    def parse_statements(self):
        # var_declaration | if | while | foreach |
        # identifier_or_call, [ "=" , condition ] | return ;
        return (
            self.parse_variable_declaration() or self.parse_if_statement()
            or self.parse_while_statement() or self.parse_foreach_statement()
            or self.parse_return_statement() or self.parse_assignment_or_function_call()
        )

    def parse_statement(self):
        # function_definition | var_declaration | if | while | foreach |
        # identifier_or_call, [ "=" , condition ] | return ;
        return (
            self.parse_function_definition() or self.parse_variable_declaration() or
            self.parse_if_statement() or self.parse_while_statement() or
            self.parse_foreach_statement() or self.parse_return_statement() or
            self.parse_assignment_or_function_call()
        )

    def parse_function_definition(self):
        # function_definition = "function" , identifier , "(" , parameters , ")" , block ;
        position = self.token.position
        if not self.must_be(TokenType.FUNCTION):
            return None

        name = self.must_be_(TokenType.IDENTIFIER, f"Expected function name in {position}")
        self.must_be_(TokenType.LEFT_PARENT, f"Expected '(' after function name in {position}")
        parameters = self.parse_parameters()
        self.must_be_(TokenType.RIGHT_PARENT, f"Expected ')' after function parameters in {position}")
        block = self.parse_block()
        return FunctionDefinition(name, parameters, block, position)

    def parse_parameters(self):
        # parameters = [ identifier , { "," , identifier } ]
        params = []
        while self.token.type == TokenType.IDENTIFIER:
            param_name = self.token.value
            self.must_be_(TokenType.IDENTIFIER, "Expected parameter type")
            params.append((param_name, TokenType.IDENTIFIER))
            if self.token.type == TokenType.COMMA:
                self.advance()
            else:
                break
        return params

    def parse_block(self):
        # block = "{", {statement}, "}";
        position = self.token.position
        if not self.must_be(TokenType.LEFT_BRACE):
            return None
        statements = []
        while statement := self.parse_statements():
            statements.append(statement)
        self.must_be_(TokenType.RIGHT_BRACE, "Expected '}' to close block")
        return Block(statements)

    def parse_foreach_statement(self):
        # foreach = "foreach", identifier, "in", (identifier | string), block;
        position = self.token.position
        if not self.must_be(TokenType.FOREACH):
            return None
        loop_variable = self.must_be_(TokenType.IDENTIFIER, f"Expected loop variable in {position}")
        self.must_be_(TokenType.IN, f"Expected 'in' {position}")
        iterable_expr = self.parse_expression()
        block = self.parse_block()
        return ForeachStatement(loop_variable, iterable_expr, block, position)

    def parse_return_statement(self):
        # return = "return", [condition];
        position = self.token.position
        if not self.must_be(TokenType.RETURN):
            return None
        value_expr = self.parse_expression()
        return ReturnStatement(value_expr, position)

    def parse_if_statement(self):
        # if = "if" , condition , block  ;
        position = self.token.position
        if not self.must_be(TokenType.IF):
            return None
        condition = self.parse_expression()
        block = self.parse_block()
        return IfStatement(condition, block, position)

    def parse_while_statement(self):
        # while = "while" , condition ,  block ;
        position = self.token.position
        if not self.must_be(TokenType.WHILE):
            return None
        condition = self.parse_expression()
        block = self.parse_block()
        return WhileStatement(condition, block, position)

    def parse_variable_declaration(self):
        # var_declaration = "value" , identifier , [ "=" , condition ] ;
        position = self.token.position

        if not self.must_be(TokenType.VALUE):
            return None

        name = self.must_be(TokenType.IDENTIFIER)
        if self.must_be(TokenType.EQUAL):
            value_expr = self.parse_expression()
        else:
            value_expr = None
        return VariableDeclaration(name, value_expr, position)

    def parse_assignment_or_function_call(self):
        # identifier_or_call = identifier , ["(", args , ")"] ;
        position = self.token.position
        if not (name := self.must_be(TokenType.IDENTIFIER)):
            return None
        if fun_call := self.parse_function_call(name):
            return fun_call
        if assignment := self.parse_assignment(name):
            return assignment
        else:
            raise SyntaxError(f"Expected '(' or '=' after identifier in {position}")

    def parse_function_call(self, name):
        # function_call = identifier , "(" , args , ")"
        position = self.token.position
        if not self.must_be(TokenType.LEFT_PARENT):
            return None
        args = self.parse_arguments()
        self.must_be_(TokenType.RIGHT_PARENT, f"Expected ')' after function arguments in {position}")
        return FunctionCall(name, args, position)

    def parse_arguments(self):
        # args =  [ condition , { "," , condition } ] ;
        args = []
        while self.token.type != TokenType.RIGHT_PARENT:
            arg = self.parse_expression()
            args.append(arg)
            if self.token.type == TokenType.COMMA:
                self.advance()
            else:
                break
        return args

    def parse_assignment(self, expression_identifier):
        # assignment = identifier , "=" , condition ;
        position = self.token.position
        if not self.must_be(TokenType.EQUAL):
            return None
        value_expr = self.parse_expression()
        return Assignment(expression_identifier, value_expr, position)

    def parse_expression(self):
        return self.parse_logical_or()

    def parse_logical_or(self):
        left_expr = self.parse_logical_and()

        while self.token.type in (TokenType.OR_OPERATOR,):
            operator = self.token.value
            position = self.token.position
            self.advance()
            right_expr = self.parse_logical_and()
            left_expr = BinaryOperation(operator, left_expr, right_expr, position)

        return left_expr

    def parse_logical_and(self):
        left_expr = self.parse_equality()

        while self.token.type in (TokenType.AND_OPERATOR,):
            operator = self.token.value
            position = self.token.position
            self.advance()
            right_expr = self.parse_equality()
            left_expr = BinaryOperation(operator, left_expr, right_expr, position)

        return left_expr

    def parse_equality(self):
        left_expr = self.parse_relational()

        while self.token.type in (TokenType.EQUALS, TokenType.NOT_EQUALS):
            operator = self.token.value
            position = self.token.position
            self.advance()
            right_expr = self.parse_relational()
            left_expr = BinaryOperation(operator, left_expr, right_expr, position)

        return left_expr

    def parse_relational(self):
        left_expr = self.parse_additive()

        while self.token.type in (
                TokenType.LESS,
                TokenType.GREATER,
                TokenType.LESS_THAN_OR_EQUAL,
                TokenType.GREATER_THAN_OR_EQUAL,
        ):
            operator = self.token.value
            position = self.token.position
            self.advance()
            right_expr = self.parse_additive()
            left_expr = BinaryOperation(operator, left_expr, right_expr, position)

        return left_expr

    def parse_additive(self):
        left_expr = self.parse_multiplicative()

        while self.token.type in (TokenType.ADD_OPERATOR, TokenType.MINUS_OPERATOR):
            operator = self.token.value
            position = self.token.position
            self.advance()
            right_expr = self.parse_multiplicative()
            left_expr = BinaryOperation(operator, left_expr, right_expr, position)

        return left_expr

    def parse_multiplicative(self):
        left_expr = self.parse_unary()

        while self.token.type in (TokenType.MULT_OPERATOR, TokenType.DIV_OPERATOR):
            operator = self.token.value
            position = self.token.position
            self.advance()
            right_expr = self.parse_unary()
            left_expr = BinaryOperation(operator, left_expr, right_expr, position)

        return left_expr

    def parse_unary(self):
        # factor = ["!" | "-"], (number | string | bool | attr_method | "(", condition, ")");
        position = self.token.position
        if operator := self.must_be(TokenType.MINUS_OPERATOR) or \
                                        self.must_be(TokenType.NEG):
            right = self.parse_primary()
            if not right:
                raise SyntaxError(f"Expected primary expression in {position}")

            return UnaryOperation(operator, right, position)
        return self.parse_primary()

    def parse_primary(self):
        return (
            self.parse_identifier() or self.parse_literal() or
            self.parse_parenthesized_expression()

        )
        # if self.token.type == TokenType.IDENTIFIER:
        #     return self.parse_identifier()
        # elif self.token.type == TokenType.INT_CONST:
        #     return self.parse_literal(TokenType.INT_CONST)
        # elif self.token.type == TokenType.FLOAT_CONST:
        #     return self.parse_literal(TokenType.FLOAT_CONST)
        # elif self.token.type == TokenType.TRUE_CONST or self.token.type == TokenType.FALSE_CONST:
        #     return self.parse_literal(TokenType.TRUE_CONST)
        # elif self.token.type == TokenType.STRING:
        #     return self.parse_literal(TokenType.STRING)
        # elif self.token.type == TokenType.LEFT_PARENT:
        #     return self.parse_parenthesized_expression()
        # else:
        #     raise SyntaxError(f"Unexpected token: {self.token.type}")

    def parse_identifier(self):
        position = self.token.position
        if not (name := self.must_be(TokenType.IDENTIFIER)):
            return None
        if self.token.type == TokenType.LEFT_PARENT:
            return self.parse_function_call(name)
        else:
            return VariableDeclaration(name, None, position)

    def parse_literal(self):
        value = self.token.value
        position = self.token.position

        if self.must_be(TokenType.INT_CONST):
            return Literal(value, TokenType.INT_CONST, position)
        if self.must_be(TokenType.FLOAT_CONST):
            return Literal(value, TokenType.FLOAT_CONST, position)
        if self.must_be(TokenType.TRUE_CONST):
            return Literal(value, TokenType.TRUE_CONST, position)
        if self.must_be(TokenType.FALSE_CONST):
            return Literal(value, TokenType.FALSE_CONST, position)
        if self.must_be(TokenType.STRING):
            return Literal(value, TokenType.STRING, position)
        return None

    def parse_parenthesized_expression(self):
        position = self.token.position
        expression = self.parse_expression()
        self.must_be_(TokenType.RIGHT_PARENT, f"Expected ')' after expression in {position}")
        return expression

    def advance(self):
        self.token = self.lexer.get_next_token()


if __name__ == "__main__":
    code = """
    function add(a, b) {
        return 42
    }
    
    if x > 5 {
        print(x)
    }
    
    while x > 1 {
        x = x + 1
    }
    
    foreach char in "word" {
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

    except SyntaxError as e:
        print(f"Syntax Error: {e}")
    except ValueError as e:
        print(f"Value Error: {e}")
