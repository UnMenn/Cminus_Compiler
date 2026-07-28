# Cminus Compiler in Python

A compiler for the C- programming language, implemented in Python. The project includes the complete compilation pipeline from lexical analysis to execution on a custom virtual machine.

## Features

- Lexical analysis using a DFA-based scanner
- LR parser that builds an Abstract Syntax Tree (AST)
- Semantic analysis with scoped symbol tables
- Three-Address Code (TAC) intermediate representation
- Control Flow Graph (CFG) construction
- Execution through a custom stack-based virtual machine
- Command-line interface with configurable compiler stages
- Unit tests using pytest

## Project Structure

```
. ├── compiler/
│ ├── cfg/ # Control Flow Graph construction
│ ├── ir/ # Three-Address Code generation and IR utilities
│ ├── lexer/ # Lexical analyzer (scanner)
│ ├── parser/ # LR parser, AST nodes, and parsing tables
│ ├── semantic/ # Semantic analysis and symbol tables
│ ├── vm/ # Virtual machine for executing compiled programs
│ └── types_states.py # Shared token, state, and compiler definitions
├── examples/ # Sample C- programs
├── tests/ # Unit tests
├── Makefile # Build, test, and clean commands
├── main.py # Compiler entry point
└── README.md
```

## Requirements
Python 3.10 or newer
pytest

## Running

Compile and execute one of the example programs:

`python main.py [file path] [flags]`

### Flag options

| Option            | Description                            |
|-------------------|----------------------------------------|
| `-h, --help`      | Display the help message and exit.     |
| `--version`       | Display the compiler version and exit. |
| `-v, --verbose`   | Enable verbose compiler output         |
| `--tokens`        | Run lexer only                         |
| `--symbols`       | Generate symbol table only             |
| `--run`           | Compile and execute                    |
| `--print-tokens`  | Print tokens while scanning            |
| `--print-ast`     | Print AST                              |
| `--print-symbols` | Print symbol table                     |
| `--print-ir`      | Print three-address code               |
| `--print-cfg`     | Print control flow graph               |

## Testing

The project includes integration tests using pytest.

Install dependencies:
Install the testing dependency:
`pip install pytest`

Currently, the project includes lexer tests.

Execute all tests with:

`make test`

or

`pytest`

## Cleaning Generated Files

Remove Python cache directories with:

`make clean`

## Example Programs

The examples/ directory contains several sample C- programs:

- `add.c-`
- `arr_sum.c-`
- `bubble_sort.c-`
- `factorial.c--`
- `gdc.c-`

These demonstrate arithmetic operations, arrays, loops, function calls, and recursion.

## Design Notes

### Lexer

The lexer implements a deterministic finite automaton (DFA) that converts the input stream into tokens.

### Parser

The parser uses an LR parsing table to construct an Abstract Syntax Tree while performing shift/reduce parsing.

### Semantic Analysis

Semantic analysis performs:

- symbol table construction
- scope management
- type checking
- function validation
- return statement verification

### Intermediate Representation

The AST is translated into Three-Address Code (TAC), providing a machine-independent intermediate representation.

### Control Flow Graph

The TAC is transformed into a Control Flow Graph, organizing instructions into basic blocks connected by control-flow edges.

### Virtual Machine

The generated CFG is executed by a custom virtual machine that supports:

- arithmetic operations
- relational operators
- variables
- arrays
- function calls
- recursion
- built-in input() and output() functions

### Planned improvements:

- Additional unit and integration tests
- Improved logging and diagnostics
- Optimization passes
- Better error recovery
