from compiler.parser.ast_nodes import *

class IRBuilder:
    def __init__(self):
        self.code = []
        self.temp_count = 0
        self.label_count = 0

    def emit(self, op, *args):
        self.code.append((op, *args))

    def new_temp(self):
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp

    def new_label(self):
        label = f"L{self.label_count}"
        self.label_count += 1
        return label


class TACGenerator:
    def __init__(self, context):
        self.ctx = context
        self.builder = IRBuilder()

    def generate(self, program):
        for decl in program.declarations:
            if isinstance(decl, FunctionDeclaration):
                self.gen_function(decl)

        return self.builder.code

    def gen_function(self, node):
        self.builder.emit("FUNC", node.name, node.return_type)

        for param in node.params:
            self.builder.emit("PARAM", param.name)

        self.emit_locals(node.body)

        self.gen_stmt(node.body)

        self.builder.emit("END_FUNC", node.name)

    def emit_locals(self, compound):

        for decl in compound.local_declarations:
            if decl.array_size is None:
                self.builder.emit("LOCAL_DECL", decl.name)

            else:
                self.builder.emit("ARRAY_DECL", decl.name, decl.array_size)

        for stmt in compound.statements:
            if isinstance(stmt, CompoundStatement):
                self.emit_locals(stmt)

    def gen_stmt(self, node):
        if node is None:
            return

        if isinstance(node, CompoundStatement):
            for stmt in node.statements:
                self.gen_stmt(stmt)

        elif isinstance(node, ExpressionStatement):
            if node.expression:
                self.gen_expr(node.expression)

        elif isinstance(node, IfStatement):
            cond = self.gen_expr(node.condition)

            if node.else_branch is None:
                end_label = self.builder.new_label()

                self.builder.emit("IFZ", cond, end_label)

                self.gen_stmt(node.then_branch)

                self.builder.emit("LABEL", end_label)

            else:
                else_label = self.builder.new_label()
                end_label = self.builder.new_label()

                self.builder.emit("IFZ", cond, else_label)

                self.gen_stmt(node.then_branch)

                self.builder.emit("GOTO", end_label)

                self.builder.emit("LABEL", else_label)

                self.gen_stmt(node.else_branch)

                self.builder.emit("LABEL", end_label)
        elif isinstance(node, WhileStatement):
            start_label = self.builder.new_label()
            end_label = self.builder.new_label()

            self.builder.emit("LABEL", start_label)

            cond = self.gen_expr(node.condition)

            self.builder.emit("IFZ", cond, end_label)

            self.gen_stmt(node.body)

            self.builder.emit("GOTO", start_label)

            self.builder.emit("LABEL", end_label)

        elif isinstance(node, ReturnStatement):
            if node.value:
                value = self.gen_expr(node.value)
                self.builder.emit("RETURN", value)
            else:
                self.builder.emit("RETURN")

    def gen_expr(self, node):
        if isinstance(node, Number):
            temp = self.builder.new_temp()
            self.builder.emit("ASSIGN", temp, node.value)
            return temp

        elif isinstance(node, Variable):
            return node.name

        elif isinstance(node, ArrayAccess):
            idx = self.gen_expr(node.index)

            temp = self.builder.new_temp()

            self.builder.emit(
                "LOAD_INDEX",
                temp,
                node.name,
                idx,
            )

            return temp

        elif isinstance(node, FunctionCall):
            args = []

            for arg in node.arguments:
                value = self.gen_expr(arg)
                args.append(value)

            function = self.ctx.get_function(node.name)

            if function and function["return_type"] == "void":
                self.builder.emit("CALL", node.name, *args)
                return None

            temp = self.builder.new_temp()
            self.builder.emit("CALL", node.name, *args, "->", temp)

            return temp
        elif isinstance(node, BinaryOp):
            if node.op == "=":
                rhs = self.gen_expr(node.right)

                if isinstance(node.left, Variable):
                    self.builder.emit(
                        "ASSIGN",
                        node.left.name,
                        rhs,
                    )

                    return node.left.name

                elif isinstance(node.left, ArrayAccess):
                    idx = self.gen_expr(node.left.index)

                    self.builder.emit(
                        "STORE_INDEX",
                        node.left.name,
                        idx,
                        rhs,
                    )

                    return rhs

            left = self.gen_expr(node.left)
            right = self.gen_expr(node.right)

            temp = self.builder.new_temp()

            op_map = {
                "+": "ADD",
                "-": "SUB",
                "*": "MUL",
                "/": "DIV",
                "<": "LT",
                "<=": "LE",
                ">": "GT",
                ">=": "GE",
                "==": "EQ",
                "!=": "NE",
            }

            tac_op = op_map[node.op]

            self.builder.emit(
                tac_op,
                temp,
                left,
                right,
            )

            return temp

        raise RuntimeError(f"Unsupported expression node: {type(node).__name__}")
