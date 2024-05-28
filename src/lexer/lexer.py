from copy import copy
from enum import Enum, auto
import sys
from io import StringIO

from errors.lexer_errors import LexerError


class TokenType(Enum):
    IF = auto()
    WHILE = auto()
    FOREACH = auto()
    IN = auto()
    VALUE = auto()
    RETURN = auto()
    FUNCTION = auto()
    IDENTIFIER = auto()
    INT_CONST = auto()
    FLOAT_CONST = auto()
    TRUE_CONST = auto()
    FALSE_CONST = auto()
    STRING = auto()
    EQUAL = auto()
    ADD_OPERATOR = auto()
    MINUS_OPERATOR = auto()
    MULT_OPERATOR = auto()
    DIV_OPERATOR = auto()
    LESS = auto()
    GREATER = auto()
    LEFT_PARENT = auto()
    RIGHT_PARENT = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    EQUALS = auto()
    NOT_EQUALS = auto()
    LESS_THAN_OR_EQUAL = auto()
    GREATER_THAN_OR_EQUAL = auto()
    AND_OPERATOR = auto()
    OR_OPERATOR = auto()
    COMMENT = auto()
    COMMA = auto()
    DOT = auto()
    NEG = auto()
    ETX = auto()


KEYWORDS = {
    'value': TokenType.VALUE,
    'if': TokenType.IF,
    'while': TokenType.WHILE,
    'foreach': TokenType.FOREACH,
    'in': TokenType.IN,
    'function': TokenType.FUNCTION,
    'return': TokenType.RETURN,
    'true': TokenType.TRUE_CONST,
    'false': TokenType.FALSE_CONST
}

OPERATORS = {
    '+': TokenType.ADD_OPERATOR,
    '-': TokenType.MINUS_OPERATOR,
    '*': TokenType.MULT_OPERATOR,
    '/': TokenType.DIV_OPERATOR,
    '(': TokenType.LEFT_PARENT,
    ')': TokenType.RIGHT_PARENT,
    '{': TokenType.LEFT_BRACE,
    '}': TokenType.RIGHT_BRACE,
    ',': TokenType.COMMA,
    '.': TokenType.DOT,
}

LOG_OPERATORS = {
    '&&': TokenType.AND_OPERATOR,
    '||': TokenType.OR_OPERATOR,
    '!': TokenType.NEG,
}

RELATION_OPERATORS = {
    '=': TokenType.EQUAL,
    '<': TokenType.LESS,
    '>': TokenType.GREATER,
    '==': TokenType.EQUALS,
    '!=': TokenType.NOT_EQUALS,
    '<=': TokenType.LESS_THAN_OR_EQUAL,
    '>=': TokenType.GREATER_THAN_OR_EQUAL,
}


class Token:
    def __init__(self, token_type, position, value=None):
        self.type = token_type
        self.position = position
        self.value = value

    def __str__(self):
        return f'Token({self.type}, Value: {repr(self.value)}, Position: Line {self.position.line}, ' \
               f'Column {self.position.column})'

    def __repr__(self):
        return self.__str__()


class Position:
    def __init__(self, line=1, column=1):
        self.line = line
        self.column = column

    def __str__(self):
        return f"Line: {self.line}, Column: {self.column}"


class CharacterReader:
    def __init__(self, source):
        self.source = source
        self.position = Position()
        self.current_char = ''

    def get_next_character(self):
        if self.current_char == '':
            pass
        elif self.current_char == '\n':
            self.position.column = 1
            self.position.line += 1
        else:
            self.position.column += 1
        self.current_char = self.source.read(1)
        # if self.current_char == '\r':
        #     pass
        return self.current_char if self.current_char else '\x03'


class Lexer:
    def __init__(self, reader, identifier_max_length=100, string_max_length=10000):
        self.STRING_MAX_LENGTH = string_max_length
        self.IDENTIFIER_MAX_LENGTH = identifier_max_length
        self.reader = reader
        self.current_char = self.reader.get_next_character()
        self.start_position = Position()

    def advance(self):
        self.current_char = self.reader.get_next_character()

    def skip_whitespace(self):
        while self.current_char.isspace():
            self.advance()

    def try_build_comment(self):
        if self.current_char == '#':
            self.advance()
            builder = []
            while self.current_char != '\n' and self.current_char != '\x03':  # ETX
                builder.append(self.current_char)
                self.advance()
            return Token(TokenType.COMMENT, self.start_position, ''.join(builder))
        return None

    def try_build_etx(self):
        if self.current_char == '\x03':
            return Token(TokenType.ETX, self.reader.position)
        return None

    def get_next_token(self):
        self.skip_whitespace()
        self.start_position = copy(self.reader.position)

        token = self.try_build_etx() \
            or self.try_build_comment() \
            or self.try_build_keyword_or_identifier() \
            or self.try_build_number() \
            or self.try_build_string() \
            or self.try_build_logical_operator('&&', TokenType.AND_OPERATOR) \
            or self.try_build_logical_operator('||', TokenType.OR_OPERATOR) \
            or self.try_build_one_or_two_char_operator('==', TokenType.EQUAL, TokenType.EQUALS) \
            or self.try_build_one_or_two_char_operator('!=', TokenType.NEG, TokenType.NOT_EQUALS) \
            or self.try_build_one_or_two_char_operator('<=', TokenType.LESS, TokenType.LESS_THAN_OR_EQUAL) \
            or self.try_build_one_or_two_char_operator('>=', TokenType.GREATER, TokenType.GREATER_THAN_OR_EQUAL) \
            or self.try_build_one_char_operator()
        if token:
            return token
        else:
            raise LexerError('Unknown token', self.start_position)

    def try_build_logical_operator(self, value, token_type):
        if self.current_char != value[0]:
            return None

        self.advance()
        if self.current_char == value[1]:
            self.advance()
            return Token(token_type, self.start_position)
        raise LexerError('Unknown token', self.start_position)

    def try_build_one_char_operator(self):
        if self.current_char in OPERATORS:
            token_type = OPERATORS[self.current_char]
            self.advance()
            return Token(token_type, self.start_position)
        return None

    def try_build_one_or_two_char_operator(self, value, one_token_char, two_token_char):
        if self.current_char != value[0]:
            return None

        self.advance()
        if self.current_char == value[1]:
            self.advance()
            return Token(two_token_char, self.start_position)
        else:
            return Token(one_token_char, self.start_position)

    def try_build_keyword_or_identifier(self):
        if self.current_char.isalpha() or self.current_char == "_":
            builder = []
            while self.current_char.isalnum() or self.current_char == "_":
                if len(builder) == self.IDENTIFIER_MAX_LENGTH:
                    raise LexerError(f"Identifier length have the maximum limit of {self.IDENTIFIER_MAX_LENGTH}",
                                     self.start_position)
                builder.append(self.current_char)
                self.advance()
            value = ''.join(builder)
            token_type = KEYWORDS.get(value, TokenType.IDENTIFIER)

            return Token(token_type, self.start_position, value)
        return None

    def try_build_number(self):
        if not self.current_char.isdecimal():
            return None

        value = int(self.current_char)
        self.advance()

        while self.current_char.isdecimal():
            if (sys.maxsize - int(self.current_char)) // 10 >= value:
                value = value * 10 + int(self.current_char)
            else:
                raise LexerError(f"Integer overflow", self.start_position)

            self.advance()

        if self.current_char != '.':
            return Token(TokenType.INT_CONST, self.start_position, value)

        self.advance()

        decimal_part = 0
        decimal_length = 0
        while self.current_char.isdecimal():
            if decimal_length > sys.float_info.dig:
                raise LexerError(f"Float overflow", self.start_position)

            decimal_part = decimal_part * 10 + int(self.current_char)
            decimal_length += 1
            self.advance()

        value += decimal_part / 10 ** decimal_length
        return Token(TokenType.FLOAT_CONST, self.start_position, value)

    def try_build_string(self):
        if self.current_char == '"':
            builder = []
            self.advance()

            while self.current_char != '"':
                if self.current_char == '\x03' or self.current_char == '\n':
                    raise LexerError(
                        f"Unterminated string literal", self.start_position)
                elif len(builder) == self.STRING_MAX_LENGTH:
                    raise ValueError(f"String length exceeds the maximum limit of {self.STRING_MAX_LENGTH} characters")

                builder.append(self.handle_escaped_character())
                self.advance()

            self.advance()

            return Token(TokenType.STRING, self.start_position, ''.join(builder))
        return None

    def handle_escaped_character(self):
        if self.current_char != '\\':
            return self.current_char
        self.advance()
        if self.current_char == 'n':
            return '\n'
        elif self.current_char == 't':
            return '\t'
        elif self.current_char == '"':
            return '"'
        elif self.current_char == '\\':
            return '\\'
        else:
            raise LexerError(f"Invalid escape character \\{self.current_char}", self.start_position)


if __name__ == '__main__':
    code = """
value x = 12.5
x = true
x = 10
value y = 5
value z = (x + y) * 2

value hello = "Hello, "
value world = "World!"
print(hello + world)
print(hello * 2)

# if statement
if z >= 10 && hello == "Hello, " {
    print("z is greater than 10 and hello is Hello, ")
}

# while loop
while x > 0 {
    print x
    x = x - 1
}

# function definition and call
function add(x, y) {
    value z = x + y
    print(z)
}

value a = 10
value b = 5
add(a, b)

# recursive function call
function recursive_add(x) {
    if x == 5 {
        return
    }
    if x >= 5 {
        x = x - 1
        recursive_add(x)
    }
}

value a = "hello"
print(a.length)         # 5

value word = input()

value c = 8
recursive_add(c)
"""

    file_name = "../input.xd"
    # lexer = Lexer(CharacterReader(StringIO(code)))
    # token = lexer.get_next_token()
    # while token.type != TokenType.ETX:
    #     print(token)
    #     token = lexer.get_next_token()
    try:
        with open(file_name, 'r') as file:
            lexer = Lexer(CharacterReader(file))
            token = lexer.get_next_token()
            while token.type != TokenType.ETX:
                print(token)
                token = lexer.get_next_token()
    except OSError:
        print(f"File {file_name} not found.")
        sys.exit()
    except StopIteration:
        pass
    except LexerError as e:
        print(e)

