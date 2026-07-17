def print_cfg(cfgs):
    for i, cfg in enumerate(cfgs):
        print(cfg.blocks)
        print(f"\n========== CFG {i} ==========\n")

        for block in cfg.blocks:
            print(f"{block.name}:")
            for instr in block.instructions:
                print("   ", instr)

            print("   preds:", [p.name for p in block.pred])
            print("   succs:", [s.name for s in block.succ])
            print()


class BasicBlock:
    def __init__(self, name):
        self.name = name
        self.instructions = []
        self.succ = []
        self.pred = []

    def __repr__(self):
        return self.name


class CFG:
    def __init__(self, name=None):
        self.name = name
        self.blocks = []
        self.entry = None

    def __repr__(self):
        return f"CFG({self.name})"


class CFGBuilder:
    def __init__(self, tac):
        self.tac = tac

    def build(self):
        cfgs = []

        for func in self.split_functions():
            cfgs.append(self.build_for_function(func))

        return cfgs

    def split_functions(self):
        functions = []
        current = None

        for instr in self.tac:
            if instr[0] == "FUNC":
                current = [instr]
            elif instr[0] == "END_FUNC":
                current.append(instr)
                functions.append(current)
                current = None
            else:
                if current is not None:
                    current.append(instr)

        return functions

    def build_for_function(self, func_tac):

        func_name = None

        for ins in func_tac:
            if ins[0] == "FUNC":
                func_name = ins[1] if len(ins) > 1 else None
                break

        if func_name is None:
            func_name = "main"

        func_tac = [i for i in func_tac if i[0] not in {"FUNC", "END_FUNC"}]

        if not func_tac:
            cfg = CFG(func_name)
            cfg.blocks = []
            cfg.entry = None
            return cfg

        label_pos = {}
        for i, ins in enumerate(func_tac):
            if ins[0] == "LABEL":
                label_pos[ins[1]] = i

        leaders = {0}

        for i, ins in enumerate(func_tac):
            op = ins[0]

            if op in {"GOTO", "IFZ"}:
                leaders.add(i)

                target = ins[1] if op == "GOTO" else ins[2]
                if target in label_pos:
                    leaders.add(label_pos[target])

                if op == "IFZ":
                    leaders.add(i + 1)

            elif op == "RETURN":
                leaders.add(i + 1)

        leaders = sorted(leaders)
        leader_set = set(leaders)

        blocks = []
        label_to_block = {}

        current = None
        block_id = 0

        for i, ins in enumerate(func_tac):
            if i in leader_set:
                current = BasicBlock(f"B{block_id}")
                block_id += 1
                blocks.append(current)

            if ins[0] == "LABEL":
                label_to_block[ins[1]] = current
                continue

            current.instructions.append(ins)

        entry = blocks[0] if blocks else None

        for i, block in enumerate(blocks):
            if not block.instructions:
                continue

            last = block.instructions[-1]
            op = last[0]

            if op == "RETURN":
                continue

            if op == "GOTO":
                tgt = last[1]
                if tgt in label_to_block:
                    self.add_edge(block, label_to_block[tgt])
                continue

            if op == "IFZ":
                tgt = last[2]

                if tgt in label_to_block:
                    self.add_edge(block, label_to_block[tgt])

                nxt = self.next_block(blocks, i)
                if nxt:
                    self.add_edge(block, nxt)

                continue

            nxt = self.next_block(blocks, i)
            if nxt:
                self.add_edge(block, nxt)

        for b in blocks:
            b.instructions = [i for i in b.instructions if i[0] != "LABEL"]

        cfg = CFG(func_name)
        cfg.blocks = blocks
        cfg.entry = entry

        return cfg

    def next_block(self, blocks, i):
        for j in range(i + 1, len(blocks)):
            if blocks[j].instructions:
                return blocks[j]
        return None

    def add_edge(self, src, dst):
        if dst not in src.succ:
            src.succ.append(dst)
        if src not in dst.pred:
            dst.pred.append(src)
