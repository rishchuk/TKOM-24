import argparse
import os
from io import StringIO

from errors.interpreter_errors import InterpreterError
from errors.lexer_errors import LexerError
from errors.parser_errors import ParserError
from interpreter.interpreter import Interpreter
from lexer.lexer import CharacterReader, Lexer
from parser.parser import Parser


def main():
    parser = argparse.ArgumentParser(description="Interpreter")
    parser.add_argument('source', nargs='?', help='Source code file (.xd) or leave empty for interactive mode')
    args = parser.parse_args()

    try:
        if args.source:
            if not args.source.endswith('.xd'):
                print("Only .xd files are supported")
                return

            if os.path.isfile(args.source):
                with open(args.source, 'r') as file:
                    code = file.read()
            else:
                print("File not found")
                return

            reader = CharacterReader(StringIO(code))
            lexer = Lexer(reader)
            parser = Parser(lexer)
            program = parser.parse_program()

            interpreter = Interpreter(program)
            interpreter.interpret()
        else:
            print("Enter /exit to finish:")
            interpreter = Interpreter(None)
            while True:
                try:
                    line = input(">>> ")
                    if line.strip() == "/exit":
                        break
                    reader = CharacterReader(StringIO(line))
                    lexer = Lexer(reader)
                    parser = Parser(lexer)
                    program = parser.parse_program()
                    interpreter.program = program
                    interpreter.interpret()

                except LexerError as e:
                    print(e)
                except ParserError as e:
                    print(e)
                except InterpreterError as e:
                    print(e)

    except LexerError as e:
        print(e)
    except ParserError as e:
        print(e)
    except InterpreterError as e:
        print(e)


if __name__ == "__main__":
    main()
