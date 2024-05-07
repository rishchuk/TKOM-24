import unittest
from parser.parser import *


class TestParser(unittest.TestCase):
    def test_parse_variable_declaration(self):
        code = """
                value x = 10
                """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser = Parser(lexer)
        program = parser.parse_program()
        self.assertEqual(len(program.functions), 1)
        var = program.functions[0]
        self.assertIsInstance(var, VariableDeclaration)
        self.assertEqual(var.name, "x")

    def test_parse_if_statement(self):
        code = """
                if x > 2 {
                    x = x + 1
                }
                """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser = Parser(lexer)
        program = parser.parse_program()
        self.assertEqual(len(program.functions), 1)
        if_stat = program.functions[0]
        self.assertIsInstance(if_stat, IfStatement)
        self.assertIsInstance(if_stat.block, Block)
        self.assertEqual(len(if_stat.block.statements), 1)

    def test_parse_while_statement(self):
        code = """
                while x < 2 {
                    x = x + 1
                }
                """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser = Parser(lexer)
        program = parser.parse_program()
        self.assertEqual(len(program.functions), 1)
        while_stat = program.functions[0]
        self.assertIsInstance(while_stat, WhileStatement)
        self.assertIsInstance(while_stat.block, Block)
        self.assertEqual(len(while_stat.block.statements), 1)

    def test_parse_foreach_statement(self):
        code = """
                foreach i in "world" {
                    print(i)
                }
                """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser = Parser(lexer)
        program = parser.parse_program()
        self.assertEqual(len(program.functions), 1)
        foreach_stat = program.functions[0]
        self.assertIsInstance(foreach_stat, ForeachStatement)
        self.assertIsInstance(foreach_stat.block, Block)
        self.assertEqual(len(foreach_stat.block.statements), 1)

    def test_parse_function_definition(self):
        code = """
                function add(a, b) {
                    return 42
                }
                """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser = Parser(lexer)
        program = parser.parse_program()
        self.assertEqual(len(program.functions), 1)
        function_def = program.functions[0]
        self.assertIsInstance(function_def, FunctionDefinition)
        self.assertEqual(function_def.name, "add")
        self.assertEqual(len(function_def.parameters), 2)
        self.assertEqual(function_def.parameters[0].name, "a")
        self.assertEqual(function_def.parameters[1].name, "b")
        self.assertIsInstance(function_def.block, Block)
        self.assertEqual(len(function_def.block.statements), 1)
        self.assertIsInstance(function_def.block.statements[0], ReturnStatement)

    def test_parse_parameters_no_params(self):
        code = """
        function foo() {
            return 42
        }
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser = Parser(lexer)
        program = parser.parse_program()
        function_def = program.functions[0]
        self.assertEqual(len(function_def.parameters), 0)

    def test_parse_block(self):
        code = """
        function foo() {
            print("Hello")
            return 42
        }
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser = Parser(lexer)
        program = parser.parse_program()
        function_def = program.functions[0]
        self.assertIsInstance(function_def.block, Block)
        self.assertEqual(len(function_def.block.statements), 2)

    def test_parse_block_empty(self):
        code = """
        function foo() {}
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser = Parser(lexer)
        program = parser.parse_program()
        function_def = program.functions[0]
        self.assertIsInstance(function_def.block, Block)
        self.assertEqual(len(function_def.block.statements), 0)

    def test_parse_function_with_if_statement(self):
        code = """
            function add(a, b) {
                if a > b {
                    b = b - a
                }
                return b
            }
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser = Parser(lexer)
        program = parser.parse_program()
        self.assertIsNotNone(program)
        self.assertIsInstance(program, Program)
        function_def = program.functions[0]
        self.assertIsInstance(function_def, FunctionDefinition)
        if_statement = function_def.block.statements[0]
        self.assertIsInstance(if_statement, IfStatement)
        if_block = if_statement.block
        self.assertIsInstance(if_block, Block)
        assignment = if_block.statements[0]
        self.assertIsInstance(assignment, Assignment)

    def test_syntax_error_expected_close_block(self):
        code = """
        function add(a, b) {
            return 42

        value result = add(x, y)
        print(result)
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Expected '}' to close block", str(context.exception))

    def test_syntax_error_expected_after_fun_params(self):
        code = """
        function add(a, b {
            return 42
        }
        value result = add(x, y)
        print(result)
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Expected ')' after function parameters", str(context.exception))

    def test_syntax_error_expected_after_fun_name(self):
        code = """
        function adda, b) {
            return 42
        }
        value result = add(x, y)
        print(result)
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Expected '(' after function name", str(context.exception))

    def test_syntax_error_expected_in_params(self):
        code = """
        function add(a, ) {
            return 42
        }
        value result = add(x, y)
        print(result)
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Expected parameter after ','", str(context.exception))

    def test_syntax_error_expected_in_args(self):
        code = """
        function add(a, b) {
            return 42
        }
        value result = add(x, )
        print(result)
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Expected argument after ','", str(context.exception))

    def test_syntax_error_expected_to_close_block(self):
        code = """
        if x > 5 {
            print(x)
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Expected '}' to close block", str(context.exception))

    def test_syntax_error_expected_loop_variable(self):
        code = """
        foreach in "word" {
            print(char)
        }
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Expected loop variable", str(context.exception))

    def test_syntax_error_expected_in(self):
        code = """
        foreach char "word" {
            print(char)
        }
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Expected 'in'", str(context.exception))

    def test_syntax_error_expected_condition(self):
        code = """
        if {}
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Expected condition", str(context.exception))

    def test_syntax_error_expected_to_open_block(self):
        code = """
        if x > 5
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Expected '{' to open block", str(context.exception))

    def test_syntax_error_expected_to_open_block_in_while(self):
        code = """
        while True 
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Expected '{' to open block", str(context.exception))

    def test_syntax_error_expected_expression_after_logical_or(self):
        code = """
        if x > 5 || {
            print(x)
        }
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Expected expression after '||'", str(context.exception))

    def test_syntax_error_expected_expression_after_logical_and(self):
        code = """
        if x > 5 && {
            print(x)
        }
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Expected expression after '&&'", str(context.exception))

    def test_syntax_error_expected_expression_after_equality(self):
        code = """
        if x == {
            print(x)
        }
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Missing second expression", str(context.exception))

    def test_syntax_error_expected_expression_after_relational(self):
        code = """
        if x > {
            print(x)
        }
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Missing second expression", str(context.exception))

    def test_syntax_error_expected_expression_after_additive(self):
        code = """
        value x = 5 +
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Missing second expression", str(context.exception))

    def test_syntax_error_expected_expression_after_multiplicative(self):
        code = """
        value x = 5 *
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Missing second expression", str(context.exception))

    def test_syntax_error_expected_expression_after_unary(self):
        code = """
        value x = !
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Missing unary expression", str(context.exception))

    def test_syntax_error_expected_attr_method_after_dot(self):
        code = """
        value x = m.
        """
        reader = CharacterReader(StringIO(code))
        lexer = Lexer(reader)
        parser_with_error = Parser(lexer)
        with self.assertRaises(SyntaxError) as context:
            parser_with_error.parse_program()
        self.assertIn("Expected identifier after '.'", str(context.exception))


if __name__ == '__main__':
    unittest.main()
