# PA 5: The Scope Resolver

Public template: https://github.com/cwillpinto/cs379-pa05-scope-resolver

Full assignment: `PA_05_The_Scope_Resolver.md`.

## Setup
Paste your own completed `lexer.py`/`parser.py`/`symtable.py` in
first (bundled here even though PA 5's new code doesn't touch lexing
or parsing directly -- `symtable.py` imports from `parser.py`, which
imports from `lexer.py`, so the whole chain has to be importable).

## Run
```bash
python test_scope_resolver.py
```
Complete `resolve_name` in `scope_resolver.py`. The harness tests
static and dynamic mode separately, checks most-recent-caller order,
checks global fallback and missing-name errors, then replays the Part A
"classic divergence" example. The Success Token prints only after every
check passes.

## Submit
1. `PA5_Theory.pdf` (or `.md`)
2. `scope_resolver.py`
3. The Success Token

Keep your working `lexer.py`, `parser.py`, and `symtable.py` in the repository
so the import chain works. You do not need to upload those inherited files to
Blackboard for PA 5.
