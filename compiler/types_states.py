from enum import Enum

# TokenType
class TokenType(Enum):
    ENDFILE = 100
    ERROR = 101
    # reserved words
    IF = "if"
    THEN = "then"
    ELSE = "else"
    RETURN = "return"
    WHILE = "while"
    INT = "int"
    VOID = "void"
    # multicharacter tokens
    ID = 200
    NUM = 201
    COMMENT = 202
    # special symbols
    ASSIGN = "="
    EQ = "=="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="
    PLUS = "+"
    MINUS = "-"
    TIMES = "*"
    OVER = "/"
    LPAREN = "("
    RPAREN = ")"
    LBRACK = "["
    RBRACK = "]"
    LBRACE = "{"
    RBRACE = "}"
    SEMI = ";"
    COMA = ","


# StateType
class StateType(Enum):
    START = 0
    INNOTEQ = 1
    INISEQ = 2
    INLEQ = 3
    INGEQ = 4
    INSLASH = 5
    INCOMMENT = 6
    ENDCOMMENT = 7
    INNUM = 8
    INID = 9
    DONE = 10


# ReservedWords
class ReservedWords(Enum):
    IF = "if"
    THEN = "then"
    ELSE = "else"
    RETURN = "return"
    WHILE = "while"
    INT = "int"
    VOID = "void"


delta = {
    # --- initial state ---
    (StateType.START, "+"): TokenType.PLUS,
    (StateType.START, "-"): TokenType.MINUS,
    (StateType.START, "*"): TokenType.TIMES,
    (StateType.START, "/"): StateType.INSLASH,
    (StateType.START, "<"): StateType.INLEQ,
    (StateType.START, ">"): StateType.INGEQ,
    (StateType.START, "="): StateType.INISEQ,
    (StateType.START, "!"): StateType.INNOTEQ,
    (StateType.START, ";"): TokenType.SEMI,
    (StateType.START, ","): TokenType.COMA,
    (StateType.START, "("): TokenType.LPAREN,
    (StateType.START, ")"): TokenType.RPAREN,
    (StateType.START, "["): TokenType.LBRACK,
    (StateType.START, "]"): TokenType.RBRACK,
    (StateType.START, "{"): TokenType.LBRACE,
    (StateType.START, "}"): TokenType.RBRACE,
    (StateType.START, "digit"): StateType.INNUM,
    (StateType.START, "letter"): StateType.INID,
    # --- identifiers ---
    (StateType.INID, "letter"): StateType.INID,
    # --- numbers ---
    (StateType.INNUM, "digit"): StateType.INNUM,
    # --- comparisons ---
    (StateType.INLEQ, "="): TokenType.LE,
    (StateType.INGEQ, "="): TokenType.GE,
    (StateType.INISEQ, "="): TokenType.EQ,
    (StateType.INNOTEQ, "="): TokenType.NE,
    # --- comments ---
    (StateType.INSLASH, "*"): StateType.INCOMMENT,
    (StateType.INCOMMENT, "*"): StateType.ENDCOMMENT,
    (StateType.INCOMMENT, "coc"): StateType.INCOMMENT,
    (StateType.INCOMMENT, "ws"): StateType.INCOMMENT,
    (StateType.INCOMMENT, "letter"): StateType.INCOMMENT,
    (StateType.INCOMMENT, "digit"): StateType.INCOMMENT,
    (StateType.ENDCOMMENT, "/"): TokenType.COMMENT,
    (StateType.ENDCOMMENT, "*"): StateType.ENDCOMMENT,
    (StateType.ENDCOMMENT, "coc"): StateType.INCOMMENT,
    (StateType.ENDCOMMENT, "ws"): StateType.INCOMMENT,
    (StateType.ENDCOMMENT, "letter"): StateType.INCOMMENT,
    (StateType.ENDCOMMENT, "digit"): StateType.INCOMMENT,
}

fallback_tokens = {
    StateType.INLEQ: TokenType.LT,
    StateType.INGEQ: TokenType.GT,
    StateType.INNOTEQ: TokenType.ERROR,
    StateType.INISEQ: TokenType.ASSIGN,
    StateType.INSLASH: TokenType.OVER,
}

OPs = [
    TokenType.PLUS,
    TokenType.MINUS,
    TokenType.TIMES,
    TokenType.OVER,
    TokenType.LT,
    TokenType.LE,
    TokenType.GT,
    TokenType.GE,
    TokenType.EQ,
    TokenType.NE,
]
