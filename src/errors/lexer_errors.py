class LexerError(Exception):
    def __init__(self, message, position):
        self.message = message
        self.position = position

    def __str__(self):
        return f"{self.message} at Line: {self.position.line}, Column: {self.position.column}"
