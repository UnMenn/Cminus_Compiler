from compiler.types_states import *
from compiler.lexer.scanner import recibeScanner, getToken
from compiler.parser.ast_nodes import *
from compiler.parser.lrtable import *

token = None # holds current token
tokenString = None # holds the token string value
Error = False
lineno = 1
SintaxTree = None
imprimeScanner = False

def syntaxError(message):
    global Error
    print(">>> Syntax error at line " + str(lineno) + ": " + message, end='')
    Error = True

def parse(imprime = True):
    global token, tokenString, lineno
    token, tokenString, lineno = getToken(imprimeScanner)

    # token, tokenString = getToken(imprimeScanner)
    while token is TokenType.COMMENT:
        token, tokenString, lineno = getToken(imprimeScanner)
        # token, tokenString = getToken(imprimeScanner)

    stack = [0]
    state = stack[-1]

    if token not in ACTION[state]:
        expected = ", ".join(t.name for t in ACTION[state].keys())

        syntaxError(
            f"Unexpected token '{tokenString}' ({token.name}). "
            f"Expected one of: {expected}"
        )
        return None

    action = ACTION[state][token]

    if action is None:
        expected = ", ".join(t.name for t in ACTION[state])
        syntaxError(
            f"Unexpected token '{tokenString}'. "
            f"Expected: {expected}"
        )
        return None

    ast_stack = []
    # print(f"STACK: {stack} | INPUT: {token} | ACTION: {action}")
    while action is not None:
        state = stack[-1]

        if token not in ACTION[state]:
            syntaxError(f"Unkown action {tokenString}")
            return None

        action = ACTION[state][token]
        # print(f"STACK: {stack} | INPUT: {token} | ACTION: {action}")

        # if action is None:
        #     return False

        if action.startswith("s"):
            next_state = int(action.split()[1])

            stack.append(token)
            stack.append(next_state)

            if token in SHIFT_BUILDERS:
                ast_stack.append(SHIFT_BUILDERS[token](tokenString, lineno))

            else:
                ast_stack.append(None)

            token, tokenString, lineno = getToken(imprimeScanner)
            # token, tokenString = getToken(imprimeScanner)
            while token is TokenType.COMMENT:
                token, tokenString, lineno = getToken(imprimeScanner)
                # token, tokenString = getToken(imprimeScanner)

        elif action.startswith("r"):
            _, rule = action.split(" ", 1)
            A, rhs = rule.split("→")
            A = A.strip()
            rhs = eval(rhs.strip())

            if rhs != []:
                children = ast_stack[-len(rhs):]
                ast_stack = ast_stack[:-len(rhs)]
            else:
                children = []

            if rhs != []:
                for _ in range(len(rhs) * 2):
                    stack.pop()

            key = (A, tuple(rhs))

            semantic_children = [c for c in children if c is not None]

            if key in REDUCE_ACTIONS:
                node = REDUCE_ACTIONS[key](semantic_children)

            elif len(semantic_children) == 1:
                node = semantic_children[0]

            else:
                node = semantic_children

            ast_stack.append(node)

            state = stack[-1]

            stack.append(A)
            stack.append(GOTO[state][A])

            # print(f"🔁 REDUCE using {A} -> {rhs}")
            # print(f"actions in table: {ACTION[GOTO[state][A]]}")

        elif action == "acc":
            # print("Accepted ☑\n")
            if Error:
                return None
            root = ast_stack[-1]

            if imprime:
                print(root.pretty())

            return root

        else:
            syntaxError("Unknown parser action")
            return None
    # if imprime:
        # printTree(t)
    # return t, Error

def recibeParser(prog, pos, long): # Recibe los globales del main
    recibeScanner(prog, pos, long) # Para mandar los globales
