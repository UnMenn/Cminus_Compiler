from collections import defaultdict, deque
from compiler.types_states import TokenType

TOKEN_MAP = {
    # identifiers / literals
    "int": TokenType.INT,
    "void": TokenType.VOID,
    "ID": TokenType.ID,
    "NUM": TokenType.NUM,

    # keywords
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "return": TokenType.RETURN,

    # punctuation
    ";": TokenType.SEMI,
    ",": TokenType.COMA,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "[": TokenType.LBRACK,
    "]": TokenType.RBRACK,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,

    # operators
    "=": TokenType.ASSIGN,
    "==": TokenType.EQ,
    "!=": TokenType.NE,
    "<": TokenType.LT,
    "<=": TokenType.LE,
    ">": TokenType.GT,
    ">=": TokenType.GE,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.TIMES,
    "/": TokenType.OVER,

    # end of input
    "$": TokenType.ENDFILE
}

# -----------------------------
# GRAMMAR
# -----------------------------
grammar = {
    "S'": [["program"]],

    "program": [["declaration_list"]],

    # declaration list (left recursion removed)
    "declaration_list": [["declaration", "declaration_list_prime"]],

    "declaration_list_prime": [
        ["declaration", "declaration_list_prime"],
        []
    ],

    "declaration": [
        ["var_declaration"],
        ["fun_declaration"]
    ],

    "type_specifier": [
        ["int"],
        ["void"]
    ],

    "var_declaration": [
        ["type_specifier", "ID", ";"],
        ["type_specifier", "ID", "[", "NUM", "]", ";"]
    ],

    "fun_declaration": [
        ["type_specifier", "ID", "(", "params", ")", "compound_stmt"]
    ],

    # params
    "params": [
        ["param_list"],
        ["void"],
        []
    ],

    "param_list": [
        ["param", "param_list_tail"]
    ],

    "param_list_tail": [
        [",", "param", "param_list_tail"],
        []
    ],

    "param": [
        ["type_specifier", "ID"],
        ["type_specifier", "ID", "[", "]"]
    ],

    # compound statement
    "compound_stmt": [
        ["{", "local_declarations", "statement_list", "}"]
    ],

    # local declarations (ε allowed)
    "local_declarations": [
        ["var_declaration", "local_declarations_prime"],
        []
    ],

    "local_declarations_prime": [
        ["var_declaration", "local_declarations_prime"],
        []
    ],

    # statement list (ε allowed)
    "statement_list": [
        ["statement", "statement_list_prime"],
        []
    ],

    "statement_list_prime": [
        ["statement", "statement_list_prime"],
        []
    ],

    # statements
    "statement": [
        ["expression_stmt"],
        ["compound_stmt"],
        ["selection_stmt"],
        ["iteration_stmt"],
        ["return_stmt"]
    ],

    "expression_stmt": [
        ["expression", ";"],
        [";"]
    ],

    # selection / iteration / return
    "selection_stmt": [
        ["if", "(", "expression", ")", "statement"],
        ["if", "(", "expression", ")", "statement", "else", "statement"]
    ],

    "iteration_stmt": [
        ["while", "(", "expression", ")", "statement"]
    ],

    "return_stmt": [
        ["return", ";"],
        ["return", "expression", ";"]
    ],

    # expressions
    "expression": [
        ["var", "=", "expression"],
        ["simple_expression"]
    ],

    "var": [
        ["ID"],
        ["ID", "[", "expression", "]"]
    ],

    "simple_expression": [
        ["additive_expression", "simple_expression_prime"]
    ],

    "simple_expression_prime": [
        ["relop", "additive_expression"],
        []
    ],

    "relop": [
        ["<="],
        ["<"],
        [">"],
        [">="],
        ["=="],
        ["!="]
    ],

    # additive expression (no left recursion)
    "additive_expression": [
        ["term", "additive_expression_prime"]
    ],

    "additive_expression_prime": [
        ["addop", "term", "additive_expression_prime"],
        []
    ],

    "addop": [
        ["+"],
        ["-"]
    ],

    # term (no left recursion)
    "term": [
        ["factor", "term_prime"]
    ],

    "term_prime": [
        ["mulop", "factor", "term_prime"],
        []
    ],

    "mulop": [
        ["*"],
        ["/"]
    ],

    # factor
    "factor": [
        ["(", "expression", ")"],
        ["var"],
        ["call"],
        ["NUM"]
    ],

    # function call + args
    "call": [
        ["ID", "(", "args", ")"]
    ],

    "args": [
        ["arg_list"],
        []
    ],

    "arg_list": [
        ["expression", "arg_list_tail"]
    ],

    "arg_list_tail": [
        [",", "expression", "arg_list_tail"],
        []
    ]
}

start_symbol = "S'"

# -----------------------------
# FIRST
# -----------------------------
def compute_first(grammar):
    FIRST = defaultdict(set)

    changed = True
    while changed:
        changed = False

        for A, prods in grammar.items():
            for prod in prods:

                if len(prod) == 0:
                    if "ε" not in FIRST[A]:
                        FIRST[A].add("ε")
                        changed = True
                    continue

                nullable = True

                for sym in prod:

                    if sym not in grammar:
                        if sym not in FIRST[A]:
                            FIRST[A].add(sym)
                            changed = True
                        nullable = False
                        break

                    before = len(FIRST[A])
                    FIRST[A] |= (FIRST[sym] - {"ε"})
                    if len(FIRST[A]) != before:
                        changed = True

                    if "ε" not in FIRST[sym]:
                        nullable = False
                        break

                if nullable:
                    FIRST[A].add("ε")

    return FIRST


FIRST = compute_first(grammar)

# -----------------------------
# FIXED FIRST(beta a)
# -----------------------------
def first_beta_a(beta, a, FIRST):
    result = set()

    for sym in beta:
        if sym not in grammar:
            result.add(sym)
            return result

        result |= (FIRST[sym] - {"ε"})

        if "ε" not in FIRST[sym]:
            return result

    result.add(a)
    return result

def first_of_sequence(seq, FIRST):
    result = set()

    for sym in seq:

        if sym not in grammar:
            result.add(sym)
            return result

        result |= (FIRST[sym] - {"ε"})

        if "ε" not in FIRST[sym]:
            return result

    result.add("ε")
    return result
# -----------------------------
# LR(1) CLOSURE (FIXED)
# -----------------------------
def closure(items, FIRST):
    items = set(items)

    while True:
        new_items = set(items)

        for (A, rhs, dot, la) in items:

            if dot >= len(rhs):
                continue

            B = rhs[dot]

            if B not in grammar:
                continue

            beta = rhs[dot + 1:]

            # --- FIX IS HERE ---
            lookaheads = first_of_sequence(beta, FIRST)

            # LR(1 RULE: if β ⇒ ε, use current lookahead
            if "ε" in lookaheads or len(beta) == 0:
                lookaheads.discard("ε")
                lookaheads.add(la)

            for prod in grammar[B]:
                for b in lookaheads:
                    new_items.add((B, tuple(prod), 0, b))

        if new_items == items:
            break

        items = new_items

    return frozenset(items)

# -----------------------------
# GOTO
# -----------------------------
def goto(items, symbol, FIRST):
    moved = set()

    for (A, rhs, dot, la) in items:
        if dot < len(rhs) and rhs[dot] == symbol:
            moved.add((A, rhs, dot + 1, la))

    if not moved:
        return frozenset()

    return closure(moved, FIRST)

# -----------------------------
# STATES
# -----------------------------
def items_collection():
    start_item = closure({("S'", tuple(grammar["S'"][0]), 0, "$")}, FIRST)

    states = [start_item]
    transitions = {}
    queue = deque([start_item])

    while queue:
        I = queue.popleft()
        i = states.index(I)

        symbols = set()
        for (_, rhs, dot, _) in I:
            if dot < len(rhs):
                symbols.add(rhs[dot])

        for sym in symbols:
            J = goto(I, sym, FIRST)

            if not J:
                continue

            if J not in states:
                states.append(J)
                queue.append(J)

            transitions[(i, sym)] = states.index(J)

    return states, transitions

# -----------------------------
# TABLES
# -----------------------------
def build_tables(states, transitions):
    ACTION = defaultdict(dict)
    GOTO = defaultdict(dict)

    for i, I in enumerate(states):

        for (A, rhs, dot, la) in I:

            # ACCEPT
            if A == "S'" and dot == len(rhs) and la == "$":
                ACTION[i][TokenType.ENDFILE] = "acc"

            # REDUCE
            elif dot == len(rhs):
                if la != "ε":
                    ACTION[i][TOKEN_MAP[la]] = f"r {A} → {list(rhs)}"

    for (s, sym), j in transitions.items():

        if sym in grammar:
            GOTO[s][sym] = j
        else:
            ACTION[s][TOKEN_MAP[sym]] = f"s {j}"

    return ACTION, GOTO

# -----------------------------
# PRINT
# -----------------------------
def print_states(states):
    print("\n=== LR(1) STATES ===")
    for i, st in enumerate(states):
        print(f"\nState {i}")
        for (A, rhs, dot, la) in st:
            print(f"  {A} -> {list(rhs[:dot])} • {list(rhs[dot:])} , {la}")

def print_tables(ACTION, GOTO):
    print("\n=== ACTION TABLE ===")
    for k in ACTION:
        print(k, ACTION[k])

    print("\n=== GOTO TABLE ===")
    for k in GOTO:
        print(k, GOTO[k])

# -----------------------------
# RUN
# -----------------------------
states, transitions = items_collection()
ACTION, GOTO = build_tables(states, transitions)

#print_states(states)
# print_tables(ACTION, GOTO)
