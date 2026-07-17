def build_func_map(cfgs):
    func_map = {}

    for cfg in cfgs:
        if cfg.name is None:
            continue
        func_map[cfg.name] = cfg

    return func_map


def new_state():
    return {"frames": [dict()], "stack": [], "ret": 0, "arrays": {}}


def frame(state):
    return state["frames"][-1]


def resolve(state, x):
    if isinstance(x, int):
        return x

    if isinstance(x, str):
        if x.isdigit() or (x.startswith("-") and x[1:].isdigit()):
            return int(x)

        if x in frame(state):
            return frame(state)[x]

        for k, v in frame(state).items():
            if k == x:
                return v

        if x in state["arrays"]:
            return state["arrays"][x]

    return 0


def set_var(state, name, val):
    frame(state)[name] = val


def exec_instr(state, ins):
    op = ins[0]

    if op == "ASSIGN":
        _, dst, src = ins
        set_var(state, dst, resolve(state, src))

    elif op == "ADD":
        _, dst, a, b = ins
        set_var(state, dst, resolve(state, a) + resolve(state, b))

    elif op == "SUB":
        _, dst, a, b = ins
        set_var(state, dst, resolve(state, a) - resolve(state, b))

    elif op == "MUL":
        _, dst, a, b = ins
        set_var(state, dst, resolve(state, a) * resolve(state, b))

    elif op == "DIV":
        _, dst, a, b = ins
        set_var(state, dst, resolve(state, a) // resolve(state, b))

    elif op == "EQ":
        _, dst, a, b = ins
        set_var(state, dst, int(resolve(state, a) == resolve(state, b)))

    elif op == "NE":
        _, dst, a, b = ins
        set_var(state, dst, int(resolve(state, a) != resolve(state, b)))

    elif op == "LT":
        _, dst, a, b = ins
        set_var(state, dst, int(resolve(state, a) < resolve(state, b)))

    elif op == "LE":
        _, dst, a, b = ins
        set_var(state, dst, int(resolve(state, a) <= resolve(state, b)))

    elif op == "GT":
        _, dst, a, b = ins
        set_var(state, dst, int(resolve(state, a) > resolve(state, b)))

    elif op == "GE":
        _, dst, a, b = ins
        set_var(state, dst, int(resolve(state, a) >= resolve(state, b)))

    elif op == "ARRAY_DECL":
        _, name, size = ins
        if name not in state["arrays"]:
            state["arrays"][name] = [0] * int(size)

    elif op == "STORE_INDEX":
        _, arr, idx, src = ins
        idx_v = resolve(state, idx)

        if arr not in state["arrays"]:
            state["arrays"][arr] = [0] * 100

        state["arrays"][arr][idx_v] = resolve(state, src)

    elif op == "LOAD_INDEX":
        _, dst, arr, idx = ins
        set_var(state, dst, state["arrays"][arr][resolve(state, idx)])

    elif op == "PARAM":
        _, name = ins

        args = frame(state).get("args", [])
        i = frame(state).get("arg_index", 0)

        val = args[i] if i < len(args) else 0

        frame(state)[name] = val
        frame(state)["arg_index"] = i + 1

    elif op == "RETURN":
        _, x = ins
        state["ret"] = resolve(state, x)


def call_function(func_map, state, name, args):

    if name == "input":
        return int(input())

    if name == "output":
        val = resolve(state, args[0]) if args else 0
        print(val)
        return 0

    cfg = func_map.get(name)
    if cfg is None:
        return 0

    state["frames"].append({"args": args, "arg_index": 0})

    for i, a in enumerate(args):
        frame(state)[f"p{i}"] = a

    param_names = []

    if hasattr(func_map[name], "param_names"):
        param_names = func_map[name].param_names

    for i, pname in enumerate(param_names):
        if i < len(args):
            frame(state)[pname] = args[i]

    ret = run_cfg(cfg, func_map, state)

    state["frames"].pop()

    return ret


def next_block(block, state):
    if not block.succ:
        return None

    last = block.instructions[-1] if block.instructions else None

    if last and last[0] == "IFZ":
        cond = resolve(state, last[1])

        # succ[0] = false branch
        # succ[1] = true branch

        if cond == 0:
            return block.succ[0]
        else:
            return block.succ[1] if len(block.succ) > 1 else block.succ[0]

    return block.succ[0]


def run_cfg(cfg, func_map, state=None):
    if state is None:
        state = new_state()

    block = cfg.entry
    if block is None:
        return 0

    while block:
        for ins in block.instructions:
            op = ins[0]

            if op == "CALL":
                func_name = ins[1]

                args = []
                dest = None

                i = 2
                n = len(ins)

                while i < n and ins[i] != "->":
                    args.append(resolve(state, ins[i]))
                    i += 1

                if i < n and ins[i] == "->":
                    i += 1

                if i < n:
                    dest = ins[i]

                ret = call_function(func_map, state, func_name, args)

                if dest is not None:
                    set_var(state, dest, ret)
            else:
                exec_instr(state, ins)

                if op == "RETURN":
                    return state["ret"]

        if not block.succ:
            break

        block = next_block(block, state)

    return state["ret"]


def run_program(cfgs):
    func_map = build_func_map(cfgs)
    state = new_state()

    if "main" not in func_map:
        raise Exception("No main function found")

    return call_function(func_map, state, "main", [])
