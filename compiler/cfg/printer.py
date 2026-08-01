def format_instruction(instr):
    op = instr[0]

    if op == "LOCAL_DECL":
        return f"local {instr[1]}"

    if op == "ARRAY_DECL":
        return f"local {instr[1]}[{instr[2]}]"

    if op == "PARAM":
        return f"param {instr[1]}"

    if op == "ASSIGN":
        _, dst, src = instr
        return f"{dst} = {src}"

    if op in {"ADD", "SUB", "MUL", "DIV", "LT", "LE", "GT", "GE", "EQ", "NE"}:

        _, dst, a, b = instr

        symbol = {
            "ADD": "+",
            "SUB": "-",
            "MUL": "*",
            "DIV": "/",
            "LT": "<",
            "LE": "<=",
            "GT": ">",
            "GE": ">=",
            "EQ": "==",
            "NE": "!=",
        }[op]

        return f"{dst} = {a} {symbol} {b}"

    if op == "LOAD_INDEX":
        _, dst, arr, idx = instr
        return f"{dst} = {arr}[{idx}]"

    if op == "STORE_INDEX":
        _, arr, idx, src = instr
        return f"{arr}[{idx}] = {src}"

    if op == "CALL":

        parts = list(instr[1:])

        if "->" in parts:
            i = parts.index("->")
            func = parts[0]
            args = parts[1:i]
            dst = parts[i + 1]
            return f"{dst} = call {func}({', '.join(map(str, args))})"

        func = parts[0]
        args = parts[1:]
        return f"call {func}({', '.join(map(str, args))})"

    if op == "RETURN":
        if len(instr) == 1:
            return "return"
        return f"return {instr[1]}"

    if op == "GOTO":
        return f"goto {instr[1]}"

    if op == "IFZ":
        _, cond, label = instr
        return f"ifz {cond} goto {label}"

    return str(instr)

def cfg_printer(cfgs):

    for i, cfg in enumerate(cfgs):

        print(f"\n========== CFG {i}: {cfg.name} ==========\n")

        print(f"Return type : {cfg.return_type}")
        print(f"Parameters  : {cfg.params}")
        print()

        for block in cfg.blocks:

            print(f"{block.name}:")

            for instr in block.instructions:
                print(f"    {format_instruction(instr)}")

            preds = ", ".join(p.name for p in block.pred) or "-"
            succs = ", ".join(s.name for s in block.succ) or "-"

            print(f"    preds: [{preds}]")
            print(f"    succs: [{succs}]")
            print()
