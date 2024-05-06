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


class Identifier(Node):
    def __init__(self, name, position):
        super().__init__(position)
        self.name = name


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
        value = self.token
        self.advance()
        return value

    def must_be_(self, expected_type, error_message):
        if self.token.type != expected_type:
            raise SyntaxError(error_message)
        value = self.token
        self.advance()
        return value

    def parse_program(self):
        statements = []
        while statement := self.parse_statement():
            statements.append(statement)

        return Program(statements)

    def parse_statements(self):
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
        if not self.must_be(TokenType.FUNCTION):
            return None

        token = self.must_be_(TokenType.IDENTIFIER, f"Expected function name")
        self.must_be_(TokenType.LEFT_PARENT, f"Expected '(' after function name")
        parameters = self.parse_parameters()
        self.must_be_(TokenType.RIGHT_PARENT, f"Expected ')' after function parameters")
        block = self.parse_block()
        return FunctionDefinition(token.value, parameters, block, position)

    def parse_parameters(self):
        # parameters = [ identifier , { "," , identifier } ]
        params = []

        if not (param := self.parse_expression()):
            return params
        params.append(param)
        while self.must_be(TokenType.COMMA):
            if not (param := self.parse_expression()):
                raise SyntaxError(f"Expected parameter after ','")
            params.append(param)
        return params

    def parse_block(self):
        # block = "{", {statement}, "}";
        position = self.token.position
        self.must_be_(TokenType.LEFT_BRACE, "Expected '{' to open block")
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
        loop_variable = self.must_be_(TokenType.IDENTIFIER, f"Expected loop variable")
        self.must_be_(TokenType.IN, f"Expected 'in'")
        if not (iterable_expr := self.parse_identifier() or self.must_be(TokenType.STRING)):
            raise SyntaxError('Must be a string variable')

        block = self.parse_block()
        return ForeachStatement(loop_variable, iterable_expr, block, position)

    def parse_return_statement(self):
        # return = "return", [ expression ];
        position = self.token.position
        if not self.must_be(TokenType.RETURN):
            return None
        value_expr = self.parse_expression()
        return ReturnStatement(value_expr, position)

    def parse_if_statement(self):
        # if = "if" , expression , block  ;
        position = self.token.position
        if not self.must_be(TokenType.IF):
            return None
        condition = self.parse_expression()
        block = self.parse_block()
        return IfStatement(condition, block, position)

    def parse_while_statement(self):
        # while = "while" , expression ,  block ;
        position = self.token.position
        if not self.must_be(TokenType.WHILE):
            return None
        condition = self.parse_expression()
        block = self.parse_block()
        return WhileStatement(condition, block, position)

    def parse_variable_declaration(self):
        # var_declaration = "value" , identifier , [ "=" , expression ] ;
        position = self.token.position

        if not self.must_be(TokenType.VALUE):
            return None

        token = self.must_be(TokenType.IDENTIFIER)
        if self.must_be(TokenType.EQUAL):
            value_expr = self.parse_expression()
        else:
            value_expr = None
        return VariableDeclaration(token.value, value_expr, position)

    def parse_assignment_or_function_call(self):
        # identifier_or_call = identifier , ["(", args , ")"] ;
        position = self.token.position
        if not (token := self.must_be(TokenType.IDENTIFIER)):
            return None
        if fun_call := self.parse_function_call(token.value, position):
            return fun_call
        if assignment := self.parse_assignment(token.value):
            return assignment
        else:
            raise SyntaxError(f"Expected '(' or '=' after identifier")

    def parse_function_call(self, name, position):
        # function_call = identifier , "(" , args , ")"
        if not self.must_be(TokenType.LEFT_PARENT):
            return None
        args = self.parse_arguments()
        self.must_be_(TokenType.RIGHT_PARENT, f"Expected ')' after function arguments")
        if self.must_be(TokenType.DOT):
            return (
                    self.parse_identifier()
            )
        return FunctionCall(name, args, position)

    def parse_arguments(self):
        # args =  [ expression , { "," , expression } ] ;
        args = []

        if not (arg := self.parse_expression()):
            return args
        args.append(arg)
        while self.must_be(TokenType.COMMA):
            if not (arg := self.parse_expression()):
                raise SyntaxError(f"Expected argument after ','")
            args.append(arg)
        return args

    def parse_assignment(self, expression_identifier):
        # assignment = identifier , "=" , expression ;
        position = self.token.position
        if not self.must_be(TokenType.EQUAL):
            return None
        value_expr = self.parse_expression()
        return Assignment(expression_identifier, value_expr, position)

    def parse_expression(self):
        return self.parse_logical_or()

    def parse_logical_or(self):
        # expression = conjuction, { logical_or , conjuction } ;
        # position = self.token.position
        if not (left_expr := self.parse_logical_and()):
            return None
        position = self.token.position
        while operator := self.must_be(TokenType.OR_OPERATOR):
            # operator = self.token.value

            if not (right_expr := self.parse_logical_and()):
                raise SyntaxError(f"Expected expression after '||'")

            left_expr = BinaryOperation(operator, left_expr, right_expr, position)

        return left_expr

    def parse_logical_and(self):
        #  conjuction = equality, { logical_and , equality} ;
        if not (left_expr := self.parse_equality()):
            return None
        position = self.token.position
        while operator := self.must_be(TokenType.AND_OPERATOR):
            if not (right_expr := self.parse_equality()):
                raise SyntaxError(f"Expected expression after '&&'")
            left_expr = BinaryOperation(operator, left_expr, right_expr, position)

        return left_expr

    def parse_equality(self):
        if not (left_expr := self.parse_relational()):
            return None
        position = self.token.position
        while operator := self.must_be(TokenType.EQUALS) or self.must_be(TokenType.NOT_EQUALS):

            if not (right_expr := self.parse_relational()):
                raise SyntaxError(f"Missing second expression")
            left_expr = BinaryOperation(operator, left_expr, right_expr, position)

        return left_expr

    def parse_relational(self):
        if not (left_expr := self.parse_additive()):
            return None
        position = self.token.position
        while operator := self.must_be(TokenType.LESS) or \
                          self.must_be(TokenType.GREATER) or \
                          self.must_be(TokenType.LESS_THAN_OR_EQUAL) or \
                          self.must_be(TokenType.GREATER_THAN_OR_EQUAL):

            if not (right_expr := self.parse_additive()):
                raise SyntaxError(f"Missing second expression")
            left_expr = BinaryOperation(operator, left_expr, right_expr, position)

        return left_expr

    def parse_additive(self):
        # additive_expression = term , { add_sub_operator , term } ;
        if not (left_expr := self.parse_multiplicative()):
            return None
        position = self.token.position
        while operator := self.must_be(TokenType.ADD_OPERATOR) or \
                          self.must_be(TokenType.MINUS_OPERATOR):

            if not (right_expr := self.parse_multiplicative()):
                raise SyntaxError(f"Missing second expression")
            left_expr = BinaryOperation(operator, left_expr, right_expr, position)

        return left_expr

    def parse_multiplicative(self):
        # term = factor , { mul_div_operator , factor } ;
        if not (left_expr := self.parse_unary()):
            return None
        position = self.token.position
        while operator := self.must_be(TokenType.MULT_OPERATOR) or \
                          self.must_be(TokenType.DIV_OPERATOR):
            if not (right_expr := self.parse_unary()):
                raise SyntaxError(f"Missing second expression")
            left_expr = BinaryOperation(operator, left_expr, right_expr, position)

        return left_expr

    def parse_unary(self):
        # factor = ["!" | "-"], (number | string | bool | attr_method | "(", expression, ")");
        position = self.token.position
        if operator := self.must_be(TokenType.MINUS_OPERATOR) or \
                       self.must_be(TokenType.NEG):
            right = self.parse_primary()
            if not right:
                raise SyntaxError(f"Missing  unary expression")

            return UnaryOperation(operator, right, position)
        return self.parse_primary()

    def parse_primary(self):
        return (
                self.parse_identifier() or self.parse_literal() or self.parse_parenthesized_expression()
        )

    def parse_identifier(self):
        position = self.token.position
        if not (token := self.must_be(TokenType.IDENTIFIER)):
            return None

        if self.token.type == TokenType.LEFT_PARENT:
            return self.parse_function_call(token.value, position)

        while self.must_be(TokenType.DOT):
            if self.token.type == TokenType.IDENTIFIER:
                return Identifier(token.value, position)
            if self.token.type == TokenType.LEFT_PARENT:
                return self.parse_function_call(token.value, position)
            raise SyntaxError(f"Expected identifier after '.'")

        return Identifier(token.value, position)

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
            while self.must_be(TokenType.DOT):
                if ident := self.parse_identifier():
                    return ident
                raise SyntaxError(f"Expected identifier after '.'")
            return Literal(value, TokenType.STRING, position)
        return None

    def parse_parenthesized_expression(self):
        position = self.token.position
        if not self.must_be(TokenType.LEFT_PARENT):
            return None
        expression = self.parse_expression()
        self.must_be_(TokenType.RIGHT_PARENT, f"Expected ')' after expression")
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

    except SyntaxError as e:
        print(f"Syntax Error: {e}")
    except ValueError as e:
        print(f"Value Error: {e}")
