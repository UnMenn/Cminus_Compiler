import copy

from compiler.parser.ast_nodes import *
from compiler.semantic.symtab import *

ctx = ProgramContext()


def semantic_error(message):
    print(f"[Semantic Error] {message}")
    return None


def print_symbol_table(symbols, scope_name):
    print(f"\n[{scope_name}]")

    for scope in symbols:
        for name, info in scope.items():
            kind = info["kind"].upper()

            if kind == "FUNCTION":
                params = []
                for p in info["params"]:
                    suffix = "[]" if p["is_array"] else ""
                    params.append(f"{p['type']}{suffix}")
                params_str = ", ".join(params)

                print(
                    f"  {name:<12} {kind:<10} returns={info['return_type']} "
                    f"params=({params_str})"
                )

            else:
                suffix = ""
                if info.get("array_size") is not None:
                    suffix = f"[{info['array_size']}]"
                elif info.get("is_array"):
                    suffix = "[]"

                offset_str = f", offset={info['offset']}" if "offset" in info else ""
                size_str = f", size={info['size']}" if "size" in info else ""
                scope_str = (
                    f", scope_level={info['scope_level']}"
                    if "scope_level" in info
                    else ""
                )
                storage_str = (
                    f", storage={info['storage']}" if "storage" in info else ""
                )

                print(
                    f"  {name:<12} {kind:<10} type={info['type']}{suffix}"
                    f"{offset_str}{size_str}{scope_str}{storage_str}"
                )


def contains_return(stmt):
    if isinstance(stmt, ReturnStatement):
        return True

    if isinstance(stmt, FunctionDeclaration):
        return any(contains_return(n) for n in stmt.body.statements)

    if isinstance(stmt, CompoundStatement):
        return any(contains_return(s) for s in stmt.statements)

    if isinstance(stmt, IfStatement):
        return contains_return(stmt.then_branch) or (
            stmt.else_branch is not None and contains_return(stmt.else_branch)
        )

    if isinstance(stmt, WhileStatement):
        return contains_return(stmt.body)

    return False


def analyze(node, table, globalSymbols):
    if isinstance(node, ReturnStatement):
        return_type = None

        for name in table[0]:
            inner_dict = table[0][name]

            if "return_type" in inner_dict:
                return_type = inner_dict["return_type"]

        value_type = node.value

        if value_type is None:
            value_type = {"type": "void"}
        else:
            value_type = analyze(node.value, table, globalSymbols)

        if not value_type:
            return None

        if value_type["type"] == return_type:
            return {"kind": "return", "type": return_type, "array_size": None}
        return semantic_error(
            f"Return type mismatch: expected '{return_type}', "
            f"got '{value_type['type']}'"
        )

    elif isinstance(node, BinaryOp):
        left = analyze(node.left, table, globalSymbols)
        right = analyze(node.right, table, globalSymbols)

        if not left or not right:
            return None

        if left.get("array_size") is not None or right.get("array_size") is not None:
            return semantic_error(
                f"Arrays cannot be used in binary operation '{node.op}'"
            )

        if left["type"] == right["type"]:
            return left
        return semantic_error(
            f"Type mismatch in binary operation '{node.op}': "
            f"{left['type']} vs {right['type']}"
        )

    elif isinstance(node, Variable):
        for scope in reversed(table):
            if node.name in scope:
                return scope[node.name]
        if node.name in globalSymbols[-1]:
            return globalSymbols[-1][node.name]
        return semantic_error(f"Undefined variable '{node.name}'")

    elif isinstance(node, ArrayAccess):
        symbol = None

        for scope in reversed(table):
            if node.name in scope:
                symbol = scope[node.name]
                break

        if symbol is None and node.name in globalSymbols[-1]:
            symbol = globalSymbols[-1][node.name]

        if symbol is None:
            return None

        if symbol.get("array_size") is None:
            return None

        index_type = analyze(node.index, table, globalSymbols)

        if not index_type:
            return None

        if index_type["type"] != "int":
            return None

        if isinstance(node.index, Number):
            if node.index.value < 0:
                return None

            if node.index.value >= symbol["array_size"]:
                return semantic_error(
                    f"Index: {node.index.value} is larger than size {symbol['array_size']}"
                )

        return {"kind": "variable", "type": symbol["type"], "array_size": None}

    elif isinstance(node, FunctionCall):
        if node.name not in globalSymbols[-1]:
            return None

        function = globalSymbols[-1][node.name]

        if function["kind"] != "function":
            return None

        params = function["params"]
        args = node.arguments

        if len(params) != len(args):
            return None

        for i in range(len(args)):
            arg_type = analyze(args[i], table, globalSymbols)

            if not arg_type:
                return None

            param_type = params[i]

            if arg_type["type"] != param_type["type"]:
                return None

            arg_is_array = arg_type.get("is_array", False)

            if arg_is_array != param_type["is_array"]:
                return None

        return {
            "kind": "function_call",
            "type": function["return_type"],
            "array_size": None,
        }

    elif isinstance(node, Number):
        return {"kind": "number", "type": "int", "array_size": None}


def unpackNode(node, symbols, globalSymbols):
    global scope_level
    if isinstance(node, FunctionDeclaration):
        for n in node.body.statements:
            unpackNode(n, symbols, globalSymbols)
    elif isinstance(node, ExpressionStatement):
        dict = analyze(node.expression, symbols, globalSymbols)
        if dict is None:
            return None
    elif isinstance(node, IfStatement):
        cond = analyze(node.condition, symbols, globalSymbols)
        if cond.get("array_size", False) or cond.get("is_array", False):
            return semantic_error("condition can not be array")
        if cond is None:
            return None
        unpackNode(node.then_branch, symbols, globalSymbols)
        if node.else_branch:
            unpackNode(node.else_branch, symbols, globalSymbols)
    elif isinstance(node, WhileStatement):
        cond = analyze(node.condition, symbols, globalSymbols)
        if cond.get("array_size", False) or cond.get("is_array", False):
            return semantic_error("condition can not be array")
        if cond is None:
            return None
        unpackNode(node.body, symbols, globalSymbols)
    elif isinstance(node, CompoundStatement):
        scope_level += 1
        new_scope = table(node, True, scope_level)

        if new_scope is not None:
            symbols.append(new_scope[-1])
            ctx.push_scope(new_scope[-1])

        for statements in node.statements:
            unpackNode(statements, symbols, globalSymbols)
            # print("cmp", n)
        if new_scope is not None:
            scope_level -= 1
            symbols.pop()
            ctx.pop_scope()
    else:
        dict = analyze(node, symbols, globalSymbols)
        if dict is None:
            return None

    return {"error": False}


def table(tree, imprime=True, scope_level=0):
    scopes = []
    scope_name = "global"

    # Collect declarations
    if isinstance(tree, Program):
        scopes = tree.declarations

    elif isinstance(tree, FunctionDeclaration):
        scopes = tree.params + tree.body.local_declarations
        scope_name = f"function {tree.name}"

    elif isinstance(tree, CompoundStatement):
        scopes = tree.local_declarations
        scope_name = "compound block"

    # Symbol table setup
    if isinstance(tree, Program):
        symbols = [ctx.globals]
    else:
        symbols = [{}]
        ctx.push_scope(symbols[-1])

    for node in scopes:
        if isinstance(node, VarDeclaration):
            if node.type_name == "void":
                return semantic_error(f"Variable '{node.name}' cannot have type void")

            if node.name in symbols[-1]:
                return semantic_error(f"Duplicate declaration of '{node.name}'")

            info = {
                "kind": "variable",
                "type": node.type_name,
                "array_size": node.array_size,
                "scope_level": scope_level,
                "storage": "local",
            }

            symbols[-1][node.name] = info
            ctx.insert(node.name, info)

        elif isinstance(node, FunctionDeclaration):
            if node.name in symbols[-1]:
                semantic_error(f"Duplicate declaration of '{node.name}'")
                continue

            params = [
                {"type": p.type_name, "is_array": p.is_array} for p in node.params
            ]

            symbols[-1][node.name] = {
                "kind": "function",
                "return_type": node.return_type,
                "params": params,
                "scope_level": scope_level,
                "label": node.name,
            }

            ctx.add_function(node.name, symbols[-1][node.name])

        elif isinstance(node, Parameter):
            if node.type_name == "void":
                return semantic_error(f"Parameter '{node.name}' cannot have type void")

            if node.name in symbols[-1]:
                return semantic_error(f"Duplicate declaration of '{node.name}'")

            info = {
                "kind": "variable",
                "type": node.type_name,
                "is_array": node.is_array,
                "scope_level": scope_level,
                "storage": "param",
            }

            symbols[-1][node.name] = info
            ctx.insert(node.name, info)

    if imprime and symbols[-1]:
        print_symbol_table(symbols, scope_name)

    return symbols


scope_level = 0


def semantica(tree, imprime=True):
    global scope_level
    functions = []
    for node in tree.declarations:
        if isinstance(node, FunctionDeclaration):
            functions.append(node)

    globalSymbols = table(tree, imprime, scope_level)

    if globalSymbols is None:
        return None

    if "main" not in globalSymbols[-1]:
        return semantic_error("Function 'main' not declared")
    elif globalSymbols[-1]["main"]["kind"] != "function":
        return semantic_error("'main' is not a function")

    ctx.globals["input"] = {
        "kind": "function",
        "return_type": "int",
        "params": [],
        "scope_level": 0,
        "label": "input",
        "builtin": True,
    }

    ctx.globals["output"] = {
        "kind": "function",
        "return_type": "void",
        "params": [
            {
                "type": "int",
                "is_array": False,
            }
        ],
        "scope_level": 0,
        "label": "output",
        "builtin": True,
    }

    globalSymbols[-1]["input"] = ctx.lookup("input")
    globalSymbols[-1]["output"] = ctx.lookup("output")

    for fun in functions:
        scope_level = 1
        symbols = table(fun, imprime, scope_level)

        if symbols is not None:
            symbols[-1][fun.name] = globalSymbols[-1][fun.name]

        if not contains_return(fun):
            return semantic_error(f"{fun.name} is missing a return statement")

        error = unpackNode(fun, symbols, globalSymbols)

        if error is None:
            return None

    return ctx
