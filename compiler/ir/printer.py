def print_tac(code):
    print("\n========== TAC ==========\n")

    for instr in code:
        op = instr[0]

        # --------------------------------------------------
        # Function begin/end
        # --------------------------------------------------

        if op == "FUNC":
            _, name, ret_type = instr
            print(f"\nfunction {name} -> {ret_type}")
            continue

        if op == "END_FUNC":
            print(f"end {instr[1]}\n")
            continue

        # --------------------------------------------------
        # Labels
        # --------------------------------------------------

        if op == "LABEL":
            print(f"{instr[1]}:")
            continue

        # --------------------------------------------------
        # Declarations
        # --------------------------------------------------

        if op == "LOCAL_DECL":
            print(f"    LOCAL {instr[1]}")
            continue

        if op == "ARRAY_DECL":
            print(f"    LOCAL {instr[1]}[{instr[2]}]")
            continue

        if op == "PARAM":
            print(f"    PARAM {instr[1]}")
            continue

        # --------------------------------------------------
        # Assignment
        # --------------------------------------------------

        if op == "ASSIGN":
            _, dst, src = instr
            print(f"    {dst} = {src}")
            continue

        # --------------------------------------------------
        # Binary ops
        # --------------------------------------------------

        if op in {"ADD", "SUB", "MUL", "DIV", "LT", "LE", "GT", "GE", "EQ", "NE"}:
            _, dst, left, right = instr

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

            print(f"    {dst} = {left} {symbol} {right}")
            continue

        # --------------------------------------------------
        # Arrays
        # --------------------------------------------------

        if op == "LOAD_INDEX":
            _, dst, arr, idx = instr
            print(f"    {dst} = {arr}[{idx}]")
            continue

        if op == "STORE_INDEX":
            _, arr, idx, value = instr
            print(f"    {arr}[{idx}] = {value}")
            continue

        # --------------------------------------------------
        # CALL (new format)
        # --------------------------------------------------

        if op == "CALL":
            parts = list(instr[1:])

            # void call: CALL func arg1 arg2 ...
            if "->" not in parts:
                func = parts[0]
                args = parts[1:]
                print(f"    CALL {func}({', '.join(map(str, args))})")
                continue

            # return call: CALL func arg1 arg2 -> temp
            arrow_index = parts.index("->")

            func = parts[0]
            args = parts[1:arrow_index]
            dst = parts[arrow_index + 1]

            print(f"    {dst} = CALL {func}({', '.join(map(str, args))})")
            continue

        # --------------------------------------------------
        # RETURN
        # --------------------------------------------------

        if op == "RETURN":
            if len(instr) == 1:
                print("    RETURN")
            else:
                print(f"    RETURN {instr[1]}")
            continue

        # --------------------------------------------------
        # Control flow
        # --------------------------------------------------

        if op == "GOTO":
            print(f"    GOTO {instr[1]}")
            continue

        if op == "IFZ":
            _, cond, label = instr
            print(f"    IFZ {cond} GOTO {label}")
            continue

        # --------------------------------------------------
        # Fallback
        # --------------------------------------------------

        print("UNKNOWN:", instr)
