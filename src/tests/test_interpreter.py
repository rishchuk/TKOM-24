import unittest

from errors.interpreter_errors import UnexpectedTypeError, TypeBinaryError, DivisionByZeroError, TypeUnaryError, \
    UndefinedVarError
from interpreter.environment import Environment
from interpreter.interpreter import Interpreter
from parser.models import IntLiteral, StringLiteral, UnaryOperation, BoolLiteral, VariableDeclaration, Identifier, \
    FloatLiteral, NullLiteral
from parser.parser import Operators


class TestInterpreter(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.interpreter = Interpreter(None)
        self.interpreter.env = self.env

    def test_binary_plus(self):
        self.assertEqual(self.interpreter.binary_plus(1, 2), 3)
        self.assertEqual(self.interpreter.binary_plus("1", 2), "12")
        self.assertEqual(self.interpreter.binary_plus(1, "2"), "12")
        self.assertEqual(self.interpreter.binary_plus("1", "2"), "12")

    def test_binary_minus(self):
        self.assertEqual(self.interpreter.binary_minus(2, 1), 1)
        with self.assertRaises(TypeBinaryError):
            self.interpreter.binary_minus("2", 1)
            self.interpreter.binary_minus(2, "1")
            self.interpreter.binary_minus("2", "1")

    def test_binary_mult(self):
        self.assertEqual(self.interpreter.binary_mult(2, 1), 2)
        self.assertEqual(self.interpreter.binary_mult("2", 2), "22")
        self.assertEqual(self.interpreter.binary_mult("2", 2), "22")
        with self.assertRaises(TypeBinaryError):
            self.interpreter.binary_mult("2", "1")

    def test_binary_div(self):
        self.assertEqual(self.interpreter.binary_div(2, 1), 2)
        with self.assertRaises(TypeBinaryError):
            self.interpreter.binary_div("2", 1)
            self.interpreter.binary_div(2, "1")
            self.interpreter.binary_div("2", "1")

        with self.assertRaises(DivisionByZeroError):
            self.interpreter.binary_div(2, 0)

    def test_comparison(self):
        self.assertEqual(self.interpreter.comparison(Operators.EQUALS, 2, 1), False)
        self.assertEqual(self.interpreter.comparison(Operators.EQUALS, "2", "2"), True)
        self.assertEqual(self.interpreter.comparison(Operators.EQUALS, "2", "1"), False)

        with self.assertRaises(TypeBinaryError):
            self.interpreter.comparison(Operators.EQUALS, "2", 2)
            self.interpreter.comparison(Operators.EQUALS, 2, "2")
            self.interpreter.comparison(Operators.LESS, "2", "1")

    def test_unary_operation(self):
        self.interpreter.visit_unary_operation(
            UnaryOperation(Operators.MINUS_OPERATOR, IntLiteral(1, None), None))
        self.assertEqual(self.interpreter.result, -1)
        self.interpreter.visit_unary_operation(
            UnaryOperation(Operators.NEG, IntLiteral(1, None), None))
        self.assertEqual(self.interpreter.result, False)
        self.interpreter.visit_unary_operation(
            UnaryOperation(Operators.NEG, StringLiteral("hello", None), None))
        self.assertEqual(self.interpreter.result, False)

        with self.assertRaises(TypeUnaryError):
            self.interpreter.visit_unary_operation(
                UnaryOperation(Operators.MINUS_OPERATOR, StringLiteral("hello", None), None))
            self.interpreter.visit_unary_operation(
                UnaryOperation(Operators.MINUS_OPERATOR, BoolLiteral("true", None), None))

    def test_logical_and(self):
        self.assertEqual(self.interpreter.logical_and(1, 0), 0)
        self.assertEqual(self.interpreter.logical_and("1", 2), 2)

    def test_logical_or(self):
        self.assertEqual(self.interpreter.logical_or(1, 0), 1)
        self.assertEqual(self.interpreter.logical_or("1", 2), '1')

    def test_identifier(self):
        self.interpreter.visit_variable_declaration(
            VariableDeclaration("x", StringLiteral(6, None), None)
        )
        self.interpreter.visit_identifier(Identifier("x", None, None))
        self.assertEqual(self.interpreter.result, 6)

    def test_int_literal(self):
        self.interpreter.visit_int_literal(IntLiteral(4, None))
        self.assertEqual(self.interpreter.result, 4)

    def test_float_literal(self):
        self.interpreter.visit_float_literal(FloatLiteral(4.2, None))
        self.assertEqual(self.interpreter.result, 4.2)

    def test_bool_literal(self):
        self.interpreter.visit_float_literal(BoolLiteral("true", None))
        self.assertEqual(self.interpreter.result, "true")

    def test_string_literal(self):
        self.interpreter.visit_float_literal(StringLiteral("hello", None))
        self.assertEqual(self.interpreter.result, "hello")

    def test_null_literal(self):
        self.interpreter.visit_float_literal(NullLiteral("null", None))
        self.assertEqual(self.interpreter.result, "null")


if __name__ == "__main__":
    unittest.main()
