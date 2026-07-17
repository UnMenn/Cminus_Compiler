import pytest

from compiler.lexer import *
from compiler.types_states import TokenType


def run_lexer(input_string):
    # Reset global state before each run
    scanner.program = input_string
    scanner.programLength = len(input_string)
    scanner.position = 0
    scanner.lineno = 1

    tokens = []
    while True:
        token, tokenString, lineno = getToken(imprime=False)
        tokens.append((token, tokenString))
        if token == TokenType.ENDFILE:
            break
    return tokens


def test_reserved_words():
    tokens = run_lexer("if then else return while int void")
    expected = [
        (TokenType.IF, "if"),
        (TokenType.THEN, "then"),
        (TokenType.ELSE, "else"),
        (TokenType.RETURN, "return"),
        (TokenType.WHILE, "while"),
        (TokenType.INT, "int"),
        (TokenType.VOID, "void"),
        (TokenType.ENDFILE, "$"),
    ]
    assert tokens == expected


def test_identifiers():
    tokens = run_lexer("x var1 testVar")
    expected = [
        (TokenType.ID, "x"),
        (TokenType.ID, "var"),
        (TokenType.NUM, "1"),  # lexer splits letters+digits
        (TokenType.ID, "testVar"),
        (TokenType.ENDFILE, "$"),
    ]
    assert tokens == expected


def test_numbers():
    tokens = run_lexer("123 4567")
    expected = [
        (TokenType.NUM, "123"),
        (TokenType.NUM, "4567"),
        (TokenType.ENDFILE, "$"),
    ]
    assert tokens == expected


def test_operators():
    tokens = run_lexer("+ - * / < <= > >= == != =")
    expected = [
        (TokenType.PLUS, "+"),
        (TokenType.MINUS, "-"),
        (TokenType.TIMES, "*"),
        (TokenType.OVER, "/"),
        (TokenType.LT, "<"),
        (TokenType.LE, "<="),
        (TokenType.GT, ">"),
        (TokenType.GE, ">="),
        (TokenType.EQ, "=="),
        (TokenType.NE, "!="),
        (TokenType.ASSIGN, "="),
        (TokenType.ENDFILE, "$"),
    ]
    assert tokens == expected


def test_symbols():
    tokens = run_lexer("() [] {} ; ,")
    expected = [
        (TokenType.LPAREN, "("),
        (TokenType.RPAREN, ")"),
        (TokenType.LBRACK, "["),
        (TokenType.RBRACK, "]"),
        (TokenType.LBRACE, "{"),
        (TokenType.RBRACE, "}"),
        (TokenType.SEMI, ";"),
        (TokenType.COMA, ","),
        (TokenType.ENDFILE, "$"),
    ]
    assert tokens == expected


def test_comment():
    tokens = run_lexer("/* this is a comment */")
    expected = [
        (TokenType.COMMENT, "/* this is a comment */"),
        (TokenType.ENDFILE, "$"),
    ]
    assert tokens == expected


def test_unclosed_comment():
    tokens = run_lexer("/* unclosed comment")
    assert tokens[0][0] in (TokenType.ERROR, TokenType.ENDFILE)


def test_error():
    tokens = run_lexer("@")
    assert tokens[0][0] == TokenType.ERROR


def test_mixed_input():
    code = "int x = 10; if (x >= 10) return x;"
    tokens = run_lexer(code)

    expected_types = [
        TokenType.INT,
        TokenType.ID,
        TokenType.ASSIGN,
        TokenType.NUM,
        TokenType.SEMI,
        TokenType.IF,
        TokenType.LPAREN,
        TokenType.ID,
        TokenType.GE,
        TokenType.NUM,
        TokenType.RPAREN,
        TokenType.RETURN,
        TokenType.ID,
        TokenType.SEMI,
        TokenType.ENDFILE,
    ]

    assert [t[0] for t in tokens] == expected_types


def test_invalid_character():
    tokens = run_lexer("@")
    assert tokens[0][0] == TokenType.ERROR


def test_invalid_mixed_sequence():
    tokens = run_lexer("abc@123")
    expected_types = [
        TokenType.ID,
        TokenType.ERROR,
        TokenType.NUM,
        TokenType.ENDFILE,
    ]
    assert [t[0] for t in tokens] == expected_types


def test_nested_comment_like_input():
    tokens = run_lexer("/* comment /* nested */ still */")
    assert any(t[0] in (TokenType.COMMENT, TokenType.ERROR) for t in tokens)


def test_lonely_exclamation():
    tokens = run_lexer("!")
    assert tokens[0][0] == TokenType.ERROR


def test_partial_operator():
    tokens = run_lexer("=")
    assert tokens[0] == (TokenType.ASSIGN, "=")


def test_weird_operator_sequence():
    tokens = run_lexer("=! =<")
    expected_types = [
        TokenType.ASSIGN,
        TokenType.ERROR,
        TokenType.ASSIGN,
        TokenType.LT,
        TokenType.ENDFILE,
    ]
    assert [t[0] for t in tokens] == expected_types


def test_identifier_followed_by_symbol():
    tokens = run_lexer("var$")
    expected_types = [
        TokenType.ID,
        TokenType.ERROR,
        TokenType.ENDFILE,
    ]
    assert [t[0] for t in tokens] == expected_types


def test_number_followed_by_letter():
    tokens = run_lexer("123abc")
    expected_types = [
        TokenType.NUM,
        TokenType.ID,
        TokenType.ENDFILE,
    ]
    assert [t[0] for t in tokens] == expected_types


def test_only_whitespace():
    tokens = run_lexer("   \n\t  ")
    assert tokens == [(TokenType.ENDFILE, "$")]


def test_empty_input():
    tokens = run_lexer("")
    assert tokens == [(TokenType.ENDFILE, "$")]


def test_comment_with_symbols_inside():
    tokens = run_lexer("/* !@#$%^&*() */")
    assert tokens[0][0] == TokenType.COMMENT


def test_comment_edge_star_slash():
    tokens = run_lexer("/**/")
    assert tokens[0][0] == TokenType.COMMENT


def test_comment_almost_closed():
    tokens = run_lexer("/* comment * not closed")
    assert tokens[0][0] in (TokenType.ERROR, TokenType.ENDFILE)


def test_multiple_errors():
    tokens = run_lexer("@ # $")
    error_count = sum(1 for t in tokens if t[0] == TokenType.ERROR)
    assert error_count >= 3
