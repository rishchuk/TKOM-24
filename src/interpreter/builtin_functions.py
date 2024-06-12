from parser.models import Statement


class PrintFun(Statement):
    name = "print"

    def accept(self, visitor, *args):
        visitor.visit_print(self, *args)


class Float(Statement):
    name = "float"

    def accept(self, visitor, value):
        visitor.visit_float(self, value)


class Bool(Statement):
    name = "bool"

    def accept(self, visitor, value):
        visitor.visit_bool(self, value)


class Str(Statement):
    name = "str"

    def accept(self, visitor, value):
        visitor.visit_str(self, value)


class ToUpper(Statement):
    name = "toUpper"

    def accept(self, visitor, value):
        visitor.visit_to_upper(self, value)


class ToLower(Statement):
    name = "toLower"

    def accept(self, visitor, value):
        visitor.visit_to_lower(self, value)


class Int(Statement):
    name = "int"

    def accept(self, visitor, value):
        visitor.visit_int(self, value)
