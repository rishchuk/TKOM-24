import io
import unittest
from contextlib import redirect_stdout
from io import StringIO

from errors.interpreter_errors import DivisionByZeroError, TypeBinaryError, UnexpectedTypeError, \
    UndefinedFunctionError, UndefinedVarError, UnexpectedMethodError
from interpreter.interpreter import Interpreter
from lexer.lexer import CharacterReader, Lexer
from parser.parser import Parser


class TestInterpreter(unittest.TestCase):
    @staticmethod
    def interpret_code(code):
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser = Parser(lexer)
        program = parser.parse_program()
        interpreter = Interpreter(program)

        f = io.StringIO()
        with redirect_stdout(f):
            interpreter.interpret()

        output = f.getvalue().strip()
        return output

    def test_var_declarations_and_assignment(self):
        code = """
        value x = 5
        print(x)
        x = "string"
        print(x)
        """
        expected_output = "5\nstring"
        self.assertEqual(self.interpret_code(code), expected_output)

    def test_function_definition_and_call(self):
        code = """
        function add(a, b) {
            return a + b
        }
        value result = add(3, 4)
        print(result)
        """
        expected_output = "7"
        self.assertEqual(self.interpret_code(code), expected_output)

    def test_return(self):
        code = """
        function add(a, b) {
            if a > b {
                return a
            }
            if b > a {
                return b
            }
            return a + b
        }
        value result = add(3, 4)
        print(result)
        """
        expected_output = "4"
        self.assertEqual(self.interpret_code(code), expected_output)

    def test_if_statement(self):
        code = """
        value x = 5
        if x > 4 {
            print("x greater than 4")
        }
        if x < 4 {
            print("x less than 4")
        }
        """
        expected_output = "x greater than 4"
        self.assertEqual(self.interpret_code(code), expected_output)

    def test_while_statement(self):
        code = """
        value x = 3
        while x > 0 {
            print(x)
            x = x - 1
        }
        """
        expected_output = "3\n2\n1"
        self.assertEqual(self.interpret_code(code), expected_output)

    def test_foreach_statement(self):
        code = """
        foreach char in "word" {
            print(char)
        }
        """
        expected_output = "w\no\nr\nd"
        self.assertEqual(self.interpret_code(code), expected_output)

    def test_builtin_functions_and_attrs(self):
        code = """
        print(int("12"))
        print(float("12.5"))
        print(bool(0))
        print(str(12))
        print("hello".toUpper())
        print("WORLD".toLower())
        print("WORLD".length)
        """
        expected_output = "12\n12.5\nfalse\n12\nHELLO\nworld\n5"
        self.assertEqual(self.interpret_code(code), expected_output)

    def test_arithmetic_and_logical_operations(self):
        code = """
        value a = 2 + 3
        value b = 10 - 2
        value c = 4 * 2
        value d = 9 / 2

        value e = 4 <= 3
        value f = 4 > 3
        value g = 5 == 5
        value h = 5 != 3
        print(a, b, c, d)
        print(e, f, g, h)
        """
        expected_output = "5 8 8 4.5\nfalse true true true"
        self.assertEqual(self.interpret_code(code), expected_output)

    def test_unary_operations(self):
        code = """
        print(!true)
        print(-5)
        """
        expected_output = "false\n-5"
        self.assertEqual(self.interpret_code(code), expected_output)

    def test_logical_or_and(self):
        code = """
        print(2 && 2)
        print(1 || 2)
        """
        expected_output = "2\n1"
        self.assertEqual(self.interpret_code(code), expected_output)

    def test_foreach_error(self):
        code = """
        foreach char in 2 {
            print(char)
        }
        """
        with self.assertRaises(UnexpectedTypeError):
            self.interpret_code(code)

    def test_div_by_zero(self):
        code = "value result = 10 / 0"
        with self.assertRaises(DivisionByZeroError):
            self.interpret_code(code)

    def test_type_bin_error(self):
        code = 'value result = "10" - 2'
        with self.assertRaises(TypeBinaryError):
            self.interpret_code(code)

    def test_unexpected_type_error(self):
        code = 'value result = int("a")'
        with self.assertRaises(UnexpectedTypeError):
            self.interpret_code(code)

    def test_unexpected_method_error(self):
        code = 'value result = "hello".f()'
        with self.assertRaises(UndefinedFunctionError):
            self.interpret_code(code)

    def test_unexpected_var_error(self):
        code = 'value result = var.length'
        with self.assertRaises(UndefinedVarError):
            self.interpret_code(code)


if __name__ == '__main__':
    unittest.main()
