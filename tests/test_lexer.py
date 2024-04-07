import io
from lexer.lexer import Lexer, CharacterReader, TokenType
import unittest
from sys import maxsize


class TestLexer(unittest.TestCase):
    def setUp(self):
        self.identifier_max_length = 100
        self.string_max_length = 10000
        self.number_nax_value = maxsize

    def test_identifier_max_length(self):
        code = io.StringIO('a' * (self.identifier_max_length + 1))
        with self.assertRaises(ValueError):
            lexer = Lexer(CharacterReader(code))
            lexer.get_next_token()

    def test_number_max_value(self):
        code = io.StringIO(str(self.number_nax_value))
        lexer = Lexer(CharacterReader(code))
        with self.assertRaises(ValueError):
            lexer.get_next_token()

    def test_string_max_length(self):
        code = io.StringIO('a' * (self.string_max_length + 1))
        lexer = Lexer(CharacterReader(code))
        with self.assertRaises(ValueError):
            lexer.get_next_token()

    def test_unterminated_string_literal(self):
        code = io.StringIO('"string')
        lexer = Lexer(CharacterReader(code))
        with self.assertRaises(SyntaxError):
            lexer.get_next_token()

    def test_count_tokens(self):
        code = io.StringIO("""
        value x
        x = 10
        value y = 5
        value z = (x + y) * 2
        """
                           )
        lexer = Lexer(CharacterReader(code))
        tokens = []
        while True:
            token = lexer.get_next_token()
            if token.type == TokenType.ETX:
                break
            tokens.append(token)
        self.assertEqual(len(tokens), 19)

    def test_valid_tokens(self):
        code = io.StringIO("""
        value x = 0.5
        value y = true
        value z = 4
        print x
        """
                           )
        lexer = Lexer(CharacterReader(code))
        tokens = [
            TokenType.VALUE,
            TokenType.IDENTIFIER,
            TokenType.EQUAL,
            TokenType.FLOAT_CONST,
            TokenType.VALUE,
            TokenType.IDENTIFIER,
            TokenType.EQUAL,
            TokenType.TRUE_CONST,
            TokenType.VALUE,
            TokenType.IDENTIFIER,
            TokenType.EQUAL,
            TokenType.INT_CONST,
            TokenType.IDENTIFIER,
            TokenType.IDENTIFIER,
            TokenType.ETX
        ]

        for token in tokens:
            self.assertEqual(lexer.get_next_token().type, token)

    def test_all_tokens(self):
        code = io.StringIO("""
        if while foreach in value return function identifier 
        10 10.5 true false "string" = + - * / < > () {} == != <= >= && || #
        $ , .
        """
                           )
        lexer = Lexer(CharacterReader(code))
        for token in TokenType:
            self.assertEqual(lexer.get_next_token().type, token)

    def test_build_undefined_token(self):
        code = io.StringIO('$va7_ue x')
        lexer = Lexer(CharacterReader(code))
        token = lexer.get_next_token()
        self.assertEqual(token.type, TokenType.UNDEFINED)
        self.assertEqual(token.value, '$va7_ue')
        self.assertEqual(token.position.line, 1)
        self.assertEqual(token.position.column, 1)

    def test_get_next_character(self):
        code = io.StringIO('value x')
        characters = CharacterReader(code)
        self.assertEqual(characters.get_next_character(), 'v')
        self.assertEqual(characters.get_next_character(), 'a')
        self.assertEqual(characters.get_next_character(), 'l')
        self.assertEqual(characters.get_next_character(), 'u')
        self.assertEqual(characters.get_next_character(), 'e')
        self.assertEqual(characters.get_next_character(), ' ')
        self.assertEqual(characters.get_next_character(), 'x')
        self.assertEqual(characters.get_next_character(), '\x03')

    def test_get_next_character_new_line(self):
        code = io.StringIO('n\nn')
        char = CharacterReader(code)
        char.get_next_character()
        self.assertEqual(char.get_next_character(), '\n')
        self.assertEqual(char.position.line, 1)
        self.assertEqual(char.position.column, 2)
        char.get_next_character()
        char.get_next_character()
        self.assertEqual(char.get_next_character(), '\x03')
        self.assertEqual(char.position.line, 2)
        self.assertEqual(char.position.column, 2)
        self.assertEqual(char.get_next_character(), '\x03')
        self.assertEqual(char.position.line, 2)
        self.assertEqual(char.position.column, 2)

    def test_peek_returns_next_character(self):
        source = io.StringIO("value")
        reader = CharacterReader(source)
        self.assertEqual(reader.peek(), 'v')
        reader.get_next_character()
        self.assertEqual(reader.peek(), 'a')
        reader.get_next_character()
        self.assertEqual(reader.peek(), 'l')
        reader.get_next_character()
        self.assertEqual(reader.peek(), 'u')
        reader.get_next_character()
        self.assertEqual(reader.peek(), 'e')
        reader.get_next_character()
        self.assertEqual(reader.peek(), '\x03')

    def test_build_int_numbers(self):
        code = io.StringIO('123')
        lexer = Lexer(CharacterReader(code))
        token = lexer.build_number(1)
        self.assertEqual(token.type, TokenType.INT_CONST)
        self.assertEqual(token.value, 123)

        code = io.StringIO('0')
        lexer = Lexer(CharacterReader(code))
        token = lexer.build_number(1)
        self.assertEqual(token.type, TokenType.INT_CONST)
        self.assertEqual(token.value, 0)

    def test_build_float_numbers(self):
        code = io.StringIO('12.5')
        lexer = Lexer(CharacterReader(code))
        token = lexer.build_number(1)
        self.assertEqual(token.type, TokenType.FLOAT_CONST)
        self.assertEqual(token.value, 12.5)

        code = io.StringIO('0.5')
        lexer = Lexer(CharacterReader(code))
        token = lexer.build_number(1)
        self.assertEqual(token.type, TokenType.FLOAT_CONST)
        self.assertEqual(token.value, 0.5)

    def test_build_string(self):
        code = io.StringIO('"12.5"')
        lexer = Lexer(CharacterReader(code))
        token = lexer.build_string(1)
        self.assertEqual(token.type, TokenType.STRING)
        self.assertEqual(token.value, "12.5")

        code = io.StringIO('"Hello !"')
        lexer = Lexer(CharacterReader(code))
        token = lexer.build_string(1)
        self.assertEqual(token.type, TokenType.STRING)
        self.assertEqual(token.value, "Hello !")

    def test_build_keyword_or_identifier(self):
        code = io.StringIO('value')
        lexer = Lexer(CharacterReader(code))
        token = lexer.build_keyword_or_identifier(1)
        self.assertEqual(token.type, TokenType.VALUE)

        code = io.StringIO('print')
        lexer = Lexer(CharacterReader(code))
        token = lexer.build_keyword_or_identifier(1)
        self.assertEqual(token.type, TokenType.IDENTIFIER)

    def test_end_token(self):
        code = io.StringIO("")
        lexer = Lexer(CharacterReader(code))
        token = lexer.get_next_token()
        self.assertEqual(token.type, TokenType.ETX)

    def test_build_string_with_escape_character(self):
        lexer = Lexer(CharacterReader(io.StringIO('"Hello,\\nWorld!"')))
        token = lexer.get_next_token()
        self.assertEqual(token.type, TokenType.STRING)
        self.assertEqual(token.value, 'Hello,\nWorld!')
        self.assertEqual(token.position.line, 1)
        self.assertEqual(token.position.column, 1)

    def test_build_string_with_invalid_escape_character(self):
        lexer = Lexer(CharacterReader(io.StringIO('"Hello,\\gWorld!"')))
        with self.assertRaises(SyntaxError):
            lexer.get_next_token()

    def test_position_tokens(self):
        code = io.StringIO("value x\n" +
                           "x = 10\n"
                           "value y = 5\n"
                           "value z = (x + y) * 2"
                           )
        lexer = Lexer(CharacterReader(code))
        token = lexer.get_next_token()
        self.assertEqual(token.value, 'value')
        self.assertEqual(token.position.line, 1)
        self.assertEqual(token.position.column, 1)

        token = lexer.get_next_token()
        self.assertEqual(token.value, 'x')
        self.assertEqual(token.position.line, 1)
        self.assertEqual(token.position.column, 7)

        token = lexer.get_next_token()
        self.assertEqual(token.value, 'x')
        self.assertEqual(token.position.line, 2)
        self.assertEqual(token.position.column, 1)

        token = lexer.get_next_token()
        self.assertEqual(token.value, None)
        self.assertEqual(token.position.line, 2)
        self.assertEqual(token.position.column, 3)

        token = lexer.get_next_token()
        self.assertEqual(token.value, 10)
        self.assertEqual(token.position.line, 2)
        self.assertEqual(token.position.column, 5)

        token = lexer.get_next_token()
        self.assertEqual(token.value, 'value')
        self.assertEqual(token.position.line, 3)
        self.assertEqual(token.position.column, 1)

    def test_peek_end_of_text(self):
        code = io.StringIO('=')
        reader = CharacterReader(code)
        reader.get_next_character()
        self.assertEqual(reader.peek(), '\x03')


if __name__ == '__main__':
    unittest.main()
