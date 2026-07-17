from compiler.types_states import TokenType
#
# ***********   Syntax tree for parsing ************

SHIFT_BUILDERS = {
    TokenType.ID: lambda s, l: TokenValue(s, l),
    TokenType.NUM: lambda s, l: TokenValue(int(s), l),
}

# =========================================================
# ASTNode
# =========================================================


class ASTNode:
    def __init__(self, line=None):
        self.line = line

    def pretty(self, level=0):
        raise NotImplementedError()


def indent(level):
    return "  " * level


# =========================================================
# Program
# =========================================================


class Program(ASTNode):
    def __init__(self, declarations=None, line=None):
        super().__init__(line)
        self.declarations = declarations or []

    def pretty(self, level=0):
        result = indent(level) + "Program\n"

        for decl in self.declarations:
            result += decl.pretty(level + 1)

        return result


# =========================================================
# Declarations
# =========================================================


class VarDeclaration(ASTNode):
    def __init__(self, type_name, name, array_size=None, line=None):
        super().__init__(line)
        self.type_name = type_name
        self.name = name
        self.array_size = array_size

    def pretty(self, level=0):
        if self.array_size is not None:
            return (
                indent(level)
                + f"VarDeclaration({self.type_name} {self.name}[{self.array_size}])\n"
            )

        return indent(level) + f"VarDeclaration({self.type_name} {self.name})\n"


class FunctionDeclaration(ASTNode):
    def __init__(self, return_type, name, params, body, line=None):
        super().__init__(line)
        self.return_type = return_type
        self.name = name
        self.params = params
        self.body = body

    def pretty(self, level=0):
        result = (
            indent(level) + f"FunctionDeclaration({self.return_type} {self.name})\n"
        )

        result += indent(level + 1) + "Parameters\n"

        for param in self.params:
            result += param.pretty(level + 2)

        result += self.body.pretty(level + 1)

        return result


class Parameter(ASTNode):
    def __init__(self, type_name, name, is_array=False, line=None):
        super().__init__(line)
        self.type_name = type_name
        self.name = name
        self.is_array = is_array

    def pretty(self, level=0):
        suffix = "[]" if self.is_array else ""

        return indent(level) + f"Parameter({self.type_name} {self.name}{suffix})\n"


# =========================================================
# Statements
# =========================================================


class CompoundStatement(ASTNode):
    def __init__(self, local_declarations=None, statements=None, line=None):
        super().__init__(line)
        self.local_declarations = local_declarations or []
        self.statements = statements or []

    def pretty(self, level=0):
        result = indent(level) + "CompoundStatement\n"

        result += indent(level + 1) + "LocalDeclarations\n"

        for decl in self.local_declarations:
            result += decl.pretty(level + 2)

        result += indent(level + 1) + "Statements\n"

        for stmt in self.statements:
            result += stmt.pretty(level + 2)

        return result


class ExpressionStatement(ASTNode):
    def __init__(self, expression=None, line=None):
        super().__init__(line)
        self.expression = expression

    def pretty(self, level=0):
        result = indent(level) + "ExpressionStatement\n"

        if self.expression:
            result += self.expression.pretty(level + 1)

        return result


class IfStatement(ASTNode):
    def __init__(self, condition, then_branch, else_branch=None, line=None):
        super().__init__(line)
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

    def pretty(self, level=0):
        result = indent(level) + "IfStatement\n"

        result += indent(level + 1) + "Condition\n"
        result += self.condition.pretty(level + 2)

        result += indent(level + 1) + "Then\n"
        result += self.then_branch.pretty(level + 2)

        if self.else_branch:
            result += indent(level + 1) + "Else\n"
            result += self.else_branch.pretty(level + 2)

        return result


class WhileStatement(ASTNode):
    def __init__(self, condition, body, line=None):
        super().__init__(line)
        self.condition = condition
        self.body = body

    def pretty(self, level=0):
        result = indent(level) + "WhileStatement\n"

        result += indent(level + 1) + "Condition\n"
        result += self.condition.pretty(level + 2)

        result += indent(level + 1) + "Body\n"
        result += self.body.pretty(level + 2)

        return result


class ReturnStatement(ASTNode):
    def __init__(self, value=None, line=None):
        super().__init__(line)
        self.value = value

    def pretty(self, level=0):
        result = indent(level) + "ReturnStatement\n"

        if self.value:
            result += self.value.pretty(level + 1)

        return result


# =========================================================
# Expressions
# =========================================================


class BinaryOp(ASTNode):
    def __init__(self, op, left, right, line=None):
        super().__init__(line)
        self.op = op
        self.left = left
        self.right = right

    def pretty(self, level=0):
        result = indent(level) + f"BinaryOp({self.op})\n"

        result += self.left.pretty(level + 1)
        result += self.right.pretty(level + 1)

        return result


class Variable(ASTNode):
    def __init__(self, name, line=None):
        super().__init__(line)
        self.name = name

    def pretty(self, level=0):
        return indent(level) + f"Variable({self.name})\n"


class ArrayAccess(ASTNode):
    def __init__(self, name, index, line=None):
        super().__init__(line)
        self.name = name
        self.index = index

    def pretty(self, level=0):
        result = indent(level) + f"ArrayAccess({self.name})\n"

        result += self.index.pretty(level + 1)

        return result


class FunctionCall(ASTNode):
    def __init__(self, name, arguments=None, line=None):
        super().__init__(line)
        self.name = name
        self.arguments = arguments or []

    def pretty(self, level=0):
        result = indent(level) + f"FunctionCall({self.name})\n"

        for arg in self.arguments:
            result += arg.pretty(level + 1)

        return result


class Number(ASTNode):
    def __init__(self, value, line=None):
        super().__init__(line)
        self.value = value

    def pretty(self, level=0):
        return indent(level) + f"Number({self.value})\n"


class TokenValue:
    def __init__(self, value, line):
        self.value = value
        self.line = line

    def __repr__(self):
        return f"TokenInfo({self.value}, line={self.line})"

REDUCE_ACTIONS = {

    # =====================================================
    # PROGRAM
    # =====================================================

    ("program", ("declaration_list",)):
        lambda c: Program(c[0], line=c[0][0].line if c[0] else None),


    # =====================================================
    # DECLARATION LISTS
    # =====================================================

    ("declaration_list",
     ("declaration", "declaration_list_prime")):
        lambda c: [c[0]] + c[1],

    ("declaration_list_prime",
     ("declaration", "declaration_list_prime")):
        lambda c: [c[0]] + c[1],

    ("declaration_list_prime", ()):
        lambda c: [],


    # =====================================================
    # DECLARATIONS
    # =====================================================

    ("declaration", ("var_declaration",)):
        lambda c: c[0],

    ("declaration", ("fun_declaration",)):
        lambda c: c[0],


    # =====================================================
    # TYPE SPECIFIER
    # =====================================================

    ("type_specifier", ("int",)):
        lambda c: "int",

    ("type_specifier", ("void",)):
        lambda c: "void",


    # =====================================================
    # VARIABLE DECLARATIONS
    # =====================================================

    ("var_declaration", ("type_specifier","ID",";")):
        lambda c: VarDeclaration(
            c[0],
            c[1].value,
            line=c[1].line
        ),

    ("var_declaration", ("type_specifier","ID","[","NUM","]",";")):
        lambda c: VarDeclaration(
            c[0],
            c[1].value,
            c[2].value,
            line=c[1].line
        ),


    # =====================================================
    # FUNCTION DECLARATION
    # =====================================================

    ("fun_declaration",
        ("type_specifier","ID","(","params",")","compound_stmt")):
            lambda c: FunctionDeclaration(
                c[0],
                c[1].value,
                c[2],
                c[3],
                line=c[1].line
            ),


    # =====================================================
    # PARAMETERS
    # =====================================================

    ("params", ("param_list",)):
        lambda c: c[0],

    ("params", ("void",)):
        lambda c: [],

    ("params", ()):
        lambda c: [],


    ("param_list",
     ("param", "param_list_tail")):
        lambda c: [c[0]] + c[1],

    ("param_list_tail",
     (",", "param", "param_list_tail")):
        lambda c: [c[0]] + c[1],

    ("param_list_tail", ()):
        lambda c: [],


    ("param", ("type_specifier","ID")):
        lambda c: Parameter(
            c[0],
            c[1].value,
            False,
            line=c[1].line
        ),

    ("param", ("type_specifier","ID","[","]")):
        lambda c: Parameter(
            c[0],
            c[1].value,
            True,
            line=c[1].line
        ),


    # =====================================================
    # COMPOUND STATEMENT
    # =====================================================

    ("compound_stmt",
     ("{", "local_declarations", "statement_list", "}")):
        lambda c: CompoundStatement(c[0], c[1]),


    # =====================================================
    # LOCAL DECLARATIONS
    # =====================================================

    ("local_declarations",
     ("var_declaration", "local_declarations_prime")):
        lambda c: [c[0]] + c[1],

    ("local_declarations", ()):
        lambda c: [],

    ("local_declarations_prime",
     ("var_declaration", "local_declarations_prime")):
        lambda c: [c[0]] + c[1],

    ("local_declarations_prime", ()):
        lambda c: [],


    # =====================================================
    # STATEMENT LISTS
    # =====================================================

    ("statement_list",
     ("statement", "statement_list_prime")):
        lambda c: [c[0]] + c[1],

    ("statement_list", ()):
        lambda c: [],

    ("statement_list_prime",
     ("statement", "statement_list_prime")):
        lambda c: [c[0]] + c[1],

    ("statement_list_prime", ()):
        lambda c: [],


    # =====================================================
    # STATEMENTS
    # =====================================================

    ("statement", ("expression_stmt",)):
        lambda c: c[0],

    ("statement", ("compound_stmt",)):
        lambda c: c[0],

    ("statement", ("selection_stmt",)):
        lambda c: c[0],

    ("statement", ("iteration_stmt",)):
        lambda c: c[0],

    ("statement", ("return_stmt",)):
        lambda c: c[0],


    # =====================================================
    # EXPRESSION STATEMENT
    # =====================================================

    ("expression_stmt", ("expression", ";")):
        lambda c: ExpressionStatement(c[0]),

    ("expression_stmt", (";",)):
        lambda c: ExpressionStatement(None),


    # =====================================================
    # IF
    # =====================================================

    ("selection_stmt", ("if","(","expression",")","statement","else","statement")):
        lambda c: IfStatement(
            c[0],
            c[1],
            c[2],
            line=c[0].line
        ),

    ("selection_stmt", ("if","(","expression",")","statement")):
        lambda c: IfStatement(
            c[0],
            c[1],
            line=c[0].line
        ),


    # =====================================================
    # WHILE
    # =====================================================

    ("iteration_stmt", ("while","(","expression",")","statement")):
        lambda c: WhileStatement(
            c[0],
            c[1],
            line=c[0].line
        ),


    # =====================================================
    # RETURN
    # =====================================================

    # kionda acá

    ("return_stmt",
     ("return", ";")):
        lambda c: ReturnStatement(),

    ("return_stmt", ("return","expression",";")):
        lambda c: ReturnStatement(
            c[0],
            line=c[0].line
        ),


    # =====================================================
    # EXPRESSIONS
    # =====================================================

    ("expression", ("var","=","expression")):
        lambda c: BinaryOp(
            "=",
            c[0],
            c[1],
            line=c[0].line
        ),

    ("expression",
     ("simple_expression",)):
        lambda c: c[0],


    # =====================================================
    # VARIABLES
    # =====================================================

    ("var", ("ID",)):
        lambda c: Variable(
            c[0].value,
            line=c[0].line
        ),

    ("var", ("ID","[","expression","]")):
        lambda c: ArrayAccess(
            c[0].value,
            c[1],
            line=c[0].line
        ),


    # =====================================================
    # SIMPLE EXPRESSIONS
    # =====================================================

    ("simple_expression",
    ("additive_expression", "simple_expression_prime")):
        lambda c: c[1](c[0]),

    ("simple_expression_prime",
     ("relop", "additive_expression")):
        lambda c: (
            lambda left:
                BinaryOp(c[0], left, c[1])
        ),

    ("simple_expression_prime", ()):
        lambda c: (lambda left: left),


    # =====================================================
    # RELOP
    # =====================================================

    ("relop", ("<",)):
        lambda c: "<",

    ("relop", ("<=",)):
        lambda c: "<=",

    ("relop", (">",)):
        lambda c: ">",

    ("relop", (">=",)):
        lambda c: ">=",

    ("relop", ("==",)):
        lambda c: "==",

    ("relop", ("!=",)):
        lambda c: "!=",


    # =====================================================
    # ADDITIVE EXPRESSIONS
    # =====================================================

    ("additive_expression",
     ("term", "additive_expression_prime")):
        lambda c: c[1](c[0]),

    ("additive_expression_prime",
     ("addop", "term", "additive_expression_prime")):
        lambda c: (
            lambda left:
                c[2](
                    BinaryOp(c[0], left, c[1])
                )
        ),

    ("additive_expression_prime", ()):
        lambda c: (
            lambda left: left
        ),


    # =====================================================
    # ADDOP
    # =====================================================

    ("addop", ("+",)):
        lambda c: "+",

    ("addop", ("-",)):
        lambda c: "-",


    # =====================================================
    # TERMS
    # =====================================================

    ("term",
     ("factor", "term_prime")):
        lambda c: c[1](c[0]),

    ("term_prime",
     ("mulop", "factor", "term_prime")):
        lambda c: (
            lambda left:
                c[2](
                    BinaryOp(c[0], left, c[1])
                )
        ),

    ("term_prime", ()):
        lambda c: (
            lambda left: left
        ),


    # =====================================================
    # MULOP
    # =====================================================

    ("mulop", ("*",)):
        lambda c: "*",

    ("mulop", ("/",)):
        lambda c: "/",


    # =====================================================
    # FACTORS
    # =====================================================

    ("factor", ("(", "expression", ")")):
        lambda c: c[0],

    ("factor", ("var",)):
        lambda c: c[0],

    ("factor", ("call",)):
        lambda c: c[0],

    ("factor", ("NUM",)):
        lambda c: Number(
            c[0].value,
            line=c[0].line
        ),


    # =====================================================
    # FUNCTION CALL
    # =====================================================

    ("call", ("ID","(","args",")")):
        lambda c: FunctionCall(
            c[0].value,
            c[1],
            line=c[0].line
        ),


    # =====================================================
    # ARGUMENTS
    # =====================================================

    ("args", ("arg_list",)):
        lambda c: c[0],

    ("args", ()):
        lambda c: [],


    ("arg_list",
     ("expression", "arg_list_tail")):
        lambda c: [c[0]] + c[1],

    ("arg_list_tail",
     (",", "expression", "arg_list_tail")):
        lambda c: [c[0]] + c[1],

    ("arg_list_tail", ()):
        lambda c: [],
}
