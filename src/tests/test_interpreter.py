import unittest

from errors.interpreter_errors import UnexpectedTypeError, TypeBinaryError, DivisionByZeroError, TypeUnaryError, \
    UndefinedVarError
from interpreter.environment import Environment
from interpreter.interpreter import Interpreter
from parser.models import IntLiteral, StringLiteral, UnaryOperation, BoolLiteral, VariableDeclaration, Identifier, \
    FloatLiteral
from parser.parser import Operators


class TestInterpreter(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.interpreter = Interpreter(None)
        self.interpreter.env = self.env

    def test_builtin_to_upper(self):
        result = self.interpreter.builtin_to_upper("hello world")
        self.assertEqual(result, "HELLO WORLD")

        with self.assertRaises(UnexpectedTypeError):
            self.interpreter.builtin_to_upper(123)

    def test_builtin_to_lower(self):
        result = self.interpreter.builtin_to_lower("HELLO WORLD")
        self.assertEqual(result, "hello world")

        with self.assertRaises(UnexpectedTypeError):
            self.interpreter.builtin_to_lower(123)

    def test_builtin_int(self):
        self.assertEqual(self.interpreter.builtin_int("12"), 12)
        self.assertEqual(self.interpreter.builtin_int(12.5), 12)
        self.assertEqual(self.interpreter.builtin_int(12), 12)

        with self.assertRaises(UnexpectedTypeError):
            self.interpreter.builtin_int("a")

    def test_builtin_float(self):
        self.assertEqual(self.interpreter.builtin_float("123.4"), 123.4)
        self.assertEqual(self.interpreter.builtin_float(123), 123.0)
        self.assertEqual(self.interpreter.builtin_float(123.4), 123.4)

        with self.assertRaises(UnexpectedTypeError):
            self.interpreter.builtin_float("a")

    def test_builtin_bool(self):
        self.assertEqual(self.interpreter.builtin_bool(0), False)
        self.assertEqual(self.interpreter.builtin_bool(1), True)
        self.assertEqual(self.interpreter.builtin_bool(""), False)
        self.assertEqual(self.interpreter.builtin_bool("a"), True)

    def test_builtin_str(self):
        self.assertEqual(self.interpreter.builtin_str(12), "12")
        self.assertEqual(self.interpreter.builtin_str(12.5), "12.5")
        self.assertEqual(self.interpreter.builtin_str(True), "True")

    def test_binary_plus(self):
        self.assertEqual(self.interpreter.binary_plus(IntLiteral(1, None), IntLiteral(2, None)), 3)
        self.assertEqual(self.interpreter.binary_plus(StringLiteral("1", None), IntLiteral(2, None)), "12")
        self.assertEqual(self.interpreter.binary_plus(IntLiteral(1, None), StringLiteral("2", None)), "12")
        self.assertEqual(self.interpreter.binary_plus(StringLiteral("1", None), StringLiteral("2", None)), "12")

    def test_binary_minus(self):
        self.assertEqual(self.interpreter.binary_minus(IntLiteral(2, None), IntLiteral(1, None)), 1)
        with self.assertRaises(TypeBinaryError):
            self.interpreter.binary_minus(StringLiteral("2", None), IntLiteral(1, None))
            self.interpreter.binary_minus(IntLiteral(2, None), StringLiteral("1", None))
            self.interpreter.binary_minus(StringLiteral("2", None), StringLiteral("1", None))

    def test_binary_mult(self):
        self.assertEqual(self.interpreter.binary_mult(IntLiteral(2, None), IntLiteral(1, None)), 2)
        self.assertEqual(self.interpreter.binary_mult(StringLiteral("2", None), IntLiteral(2, None)), "22")
        self.assertEqual(self.interpreter.binary_mult(StringLiteral("2", None), IntLiteral(2, None)), "22")
        with self.assertRaises(TypeBinaryError):
            self.interpreter.binary_mult(StringLiteral("2", None), StringLiteral("1", None))

    def test_binary_div(self):
        self.assertEqual(self.interpreter.binary_div(IntLiteral(2, None), IntLiteral(1, None)), 2)
        with self.assertRaises(TypeBinaryError):
            self.interpreter.binary_div(StringLiteral("2", None), IntLiteral(1, None))
            self.interpreter.binary_div(IntLiteral(2, None), StringLiteral("1", None))
            self.interpreter.binary_div(StringLiteral("2", None), StringLiteral("1", None))

        with self.assertRaises(DivisionByZeroError):
            self.interpreter.binary_div(IntLiteral(2, None), IntLiteral(0, None))

    def test_comparison(self):
        self.assertEqual(self.interpreter.comparison(Operators.EQUALS, IntLiteral(2, None), IntLiteral(1, None)), False)
        self.assertEqual(self.interpreter.comparison(Operators.EQUALS, StringLiteral("2", None), IntLiteral("2", None)), True)
        self.assertEqual(self.interpreter.comparison(Operators.EQUALS, StringLiteral("2", None), StringLiteral("1", None)), False)

        with self.assertRaises(TypeBinaryError):
            self.interpreter.comparison(Operators.EQUALS, StringLiteral("2", None), IntLiteral(2, None))
            self.interpreter.comparison(Operators.EQUALS, IntLiteral(2, None), StringLiteral("2", None))
            self.interpreter.comparison(Operators.LESS, StringLiteral("2", None), StringLiteral("1", None))

    def test_unary_operation(self):
        self.assertEqual(self.interpreter.visit_unary_operation(
            UnaryOperation(Operators.MINUS_OPERATOR, IntLiteral(1, None), None)), -1)
        self.assertEqual(self.interpreter.visit_unary_operation(
            UnaryOperation(Operators.NEG, IntLiteral(1, None), None)), False)
        self.assertEqual(self.interpreter.visit_unary_operation(
            UnaryOperation(Operators.NEG, StringLiteral("hello", None), None)), False)

        with self.assertRaises(TypeUnaryError):
            self.interpreter.visit_unary_operation(
                UnaryOperation(Operators.MINUS_OPERATOR, StringLiteral("hello", None), None))
            self.interpreter.visit_unary_operation(
                UnaryOperation(Operators.MINUS_OPERATOR, BoolLiteral("true", None), None))

    def test_logical_and(self):
        self.assertEqual(self.interpreter.logical_and(IntLiteral(1, None), IntLiteral(0, None)), 0)
        self.assertEqual(self.interpreter.logical_and(StringLiteral("1", None), IntLiteral(2, None)), 2)

    def test_logical_or(self):
        self.assertEqual(self.interpreter.logical_or(IntLiteral(1, None), IntLiteral(0, None)), 1)
        self.assertEqual(self.interpreter.logical_or(StringLiteral("1", None), IntLiteral(2, None)), '1')

    def test_identifier(self):
        self.interpreter.visit_variable_declaration(
            VariableDeclaration("x", StringLiteral(6, None), None)
        )
        self.assertEqual(self.interpreter.visit_identifier(
            Identifier("x", None, None)), 6)

    def test_int_literal(self):
        self.assertEqual(
            self.interpreter.visit_int_literal(IntLiteral(4, None)), 4
        )

    def test_float_literal(self):
        self.assertEqual(
            self.interpreter.visit_float_literal(FloatLiteral(4.2, None)), 4.2
        )


if __name__ == "__main__":
    unittest.main()
