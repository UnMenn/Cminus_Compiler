import argparse
import sys

from compiler.lexer import recibeScanner, getToken
from compiler.parser import parse, recibeParser
from compiler.semantic import *
from compiler.ir import TACGenerator, print_tac
from compiler.cfg import CFGBuilder
from compiler.vm import run_program

def load_program(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' does not exist.", file=sys.stderr)
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied when reading '{filename}'.", file=sys.stderr)
        sys.exit(1)
    except OSError as e:
        print(f"Error: Could not read '{filename}': {e}", file=sys.stderr)
        sys.exit(1)

def log(message, verbose):
    if verbose:
        print(message)

def lexer(program, print_tokens=False, verbose=False):
    log("[Scanner] Starting lexical analysis...", verbose)

    position = 0
    progLong = len(program)

    recibeScanner(program, position, progLong)

    token, tokenString, lineno = getToken(print_tokens)

    while token != TokenType.ENDFILE:
        token, tokenString, lineno = getToken(print_tokens)

    log("[Scanner] Finished.", verbose)


def parse_program(program, print_ast=False, verbose=False):
    log("[Parser] Building AST...", verbose)

    position = 0
    progLong = len(program)

    recibeParser(program, position, progLong)

    ast = parse(print_ast)

    log("[Parser] Finished.", verbose)

    return ast


def generate_symbols(program, print_symbols=False, verbose=False):
    log("[Semantic] Checking program...", verbose)

    ast = parse_program(program, False, verbose)

    if ast is not None:
        semantica(ast, print_symbols)

    log("[Semantic] Finished.", verbose)


def compile_program(
        program,
        print_tokens=False,
        print_ast=False,
        print_symbols=False,
        print_ir=False,
        verbose=False
):

    log("[Compiler] Starting compilation...", verbose)

    if print_tokens:
        lexer(program, print_tokens=True, verbose=verbose)

    ast = parse_program(
        program,
        print_ast,
        verbose
    )

    if ast is not None:

        log("[Semantic] Running semantic analysis...", verbose)

        ctx = semantica(
            ast,
            print_symbols
        )

        if ctx is not None:

            log("[IR] Generating TAC...", verbose)

            generator = TACGenerator(ctx)
            code = generator.generate(ast)

            if print_ir:
                print_tac(code)

            log("[CFG] Building control flow graph...", verbose)

            cfg_builder = CFGBuilder(code)
            cfg = cfg_builder.build()

            log("[VM] Running program...", verbose)

            run_program(cfg)

    log("[Compiler] Finished.", verbose)


def main():
    parser = argparse.ArgumentParser(
        description="Compiler for C- language"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="C- Compiler 1.0"
    )

    parser.add_argument(
        "file",
        help="C- source file"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose compiler output"
    )

    # Compiler actions
    parser.add_argument(
        "--tokens",
        action="store_true",
        help="Run lexer only"
    )

    parser.add_argument(
        "--symbols",
        action="store_true",
        help="Generate symbol table only"
    )

    parser.add_argument(
        "--run",
        action="store_true",
        help="Compile and execute"
    )

    # Output controls
    parser.add_argument(
        "--print-tokens",
        action="store_true",
        help="Print tokens while scanning"
    )

    parser.add_argument(
        "--print-ast",
        action="store_true",
        help="Print AST"
    )

    parser.add_argument(
        "--print-symbols",
        action="store_true",
        help="Print symbol table"
    )

    parser.add_argument(
        "--print-ir",
        action="store_true",
        help="Print three-address code"
    )


    args = parser.parse_args()

    program = load_program(args.file)

    if args.tokens:
        lexer(program, args.print_tokens)

    elif args.symbols:
        generate_symbols(
            program,
            args.print_symbols
        )

    else:
        compile_program(
            program,
            print_tokens=args.print_tokens,
            print_ast=args.print_ast,
            print_symbols=args.print_symbols,
            print_ir=args.print_ir,
            verbose=args.verbose
        )

if __name__ == "__main__":
    main()
