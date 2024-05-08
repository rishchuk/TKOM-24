
class ParserError(Exception):
    def __init__(self, error_message, position):
        super().__init__(error_message)
        self.position = position

    def __str__(self):
        return f'{super().__str__()}: {self.position}'


class UnexpectedTokenError(ParserError):
    def __init__(self, position):
        super().__init__('Unexpected token type', position)


class ExpectedFunctionNameError(ParserError):
    def __init__(self, position):
        super().__init__('Expected function name', position)


class ExpectedLeftParentAfterFun(ParserError):
    def __init__(self, position):
        super().__init__('Expected \'(\' after function name', position)


class ExpectedRightParentAfterFun(ParserError):
    def __init__(self, position):
        super().__init__('Expected \')\' after function parameters', position)


class ExpectedBlockError(ParserError):
    def __init__(self, position):
        super().__init__('Expected block', position)


class ExpectedParameterAfterCommaError(ParserError):
    def __init__(self, position):
        super().__init__('Expected parameter after \',\'', position)


class ExpectedRightBraceError(ParserError):
    def __init__(self, position):
        super().__init__('Expected \'}\' to close block', position)


class ExpectedLoopVariableError(ParserError):
    def __init__(self, position):
        super().__init__('Expected loop variable', position)


class ExpectedInError(ParserError):
    def __init__(self, position):
        super().__init__('Expected \'in\'', position)


class ExpectedExpressionError(ParserError):
    def __init__(self, position):
        super().__init__('Must be an expression', position)


class ExpectedConditionError(ParserError):
    def __init__(self, position):
        super().__init__('Expected condition', position)


class ExpectedVariableNameError(ParserError):
    def __init__(self, position):
        super().__init__("Expected variable name", position)


class ExpectedAssignmentOrFunctionCall(ParserError):
    def __init__(self, position):
        super().__init__("Expected '(' or '=' after identifier", position)


class ExpectedRightParentAfterFunCall(ParserError):
    def __init__(self, position):
        super().__init__('Expected \')\' to close function call', position)


class ExpectedArgumentAfterCommaError(ParserError):
    def __init__(self, position):
        super().__init__('Expected argument after \',\'', position)


class ExpectedRightParentAfterExpression(ParserError):
    def __init__(self, position):
        super().__init__('Expected \')\' after expression', position)


class ExpectedIdentifierAfterDotError(ParserError):
    def __init__(self, position):
        super().__init__('Expected identifier after \'.\'', position)
