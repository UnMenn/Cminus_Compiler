from compiler.types_states import *

lineno = 1

def recibeScanner(prog, pos, long):
    global program
    global position
    global programLength
    program = prog
    position = pos
    programLength = long

def reservedLookup(tokenString):
    for w in ReservedWords:
        if tokenString == w.value:
            return TokenType(tokenString)
    return TokenType.ID

def classify(char, state):
    # Inside comments: everything is "coc" except * and /
    if state in (StateType.INCOMMENT, StateType.ENDCOMMENT):
        if char == '*' and state == StateType.INCOMMENT:
            return '*'
        elif char == '/' and state == StateType.ENDCOMMENT:
            return '/'
        else:
            return 'coc'

    if char.isdigit():
        return "digit"
    elif char.isalpha():
        return "letter"
    elif char in "+-*/<>=!;,()[]{}":
        return char
    elif char.isspace():
        return "ws"
    else:
        return "coc"

def finalize_token(state, lexema, reserved_words, imprime, lineno):
    # identifiers / reserved words
    if state == StateType.INID:
        if lexema in reserved_words:
            token = TokenType(lexema)
        else:
            token = TokenType.ID

        if imprime:
            print(f"Token: {token}, lexema: {lexema}")
        return token, lexema, lineno

    # numbers
    if state == StateType.INNUM:
        if imprime:
            print(f"Token: {TokenType.NUM}, lexema: {lexema}")
        return TokenType.NUM, lexema, lineno

    # fallback tokens (e.g. <, >, =, /)
    if state in fallback_tokens:
        token = fallback_tokens[state]
        if imprime:
            print(f"Token: {token}, lexema: {lexema}")
        return token, lexema, lineno

    return None  # nothing to finalize

def getToken(imprime = True):
    global position, lineno
    reserved_words = [reserved.value for reserved in ReservedWords]
    lexema = "" # string for storing token
    currentToken = None # is a TokenType value
    state = StateType.START # current state - always begins at START
    while (state != StateType.DONE):
        if position >= programLength:
            result = finalize_token(state, lexema, reserved_words, imprime, lineno)
            if result:
                return result

            return TokenType.ENDFILE, "$", lineno
        c = program[position]
        symbol = classify(c, state)
        if symbol == "ws" and state == StateType.START:
            if c == "\n":
                lineno += 1
            position += 1
            continue

        key = (state, symbol)

        if key not in delta:
            result = finalize_token(state, lexema, reserved_words, imprime, lineno)
            if result is not None:
                return result

            lexema += c
            position += 1
            if imprime:
                print(f"Línea {lineno}: Error léxico: {lexema}")
            return TokenType.ERROR, lexema, lineno
        next_state = delta[key]

        if isinstance(next_state, TokenType):
            lexema += c
            position += 1
            if imprime:
                print(f"Token: {next_state}, lexema: {lexema}")
            return next_state, lexema, lineno

        state = next_state
        lexema += c
        position += 1
