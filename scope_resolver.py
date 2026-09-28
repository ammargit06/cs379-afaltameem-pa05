"""
PA 5: The Scope Resolver -- starter.

Complete resolve_name below. See the assignment, Part B,
for the full requirements.
"""

from typing import List

from symtable import Environment, SemanticError


def resolve_name(
    name: str,
    current_env: Environment,
    call_stack: List[Environment],
    mode: str,
) -> int:
    """
    Return the declaration line `name` resolves to.

    mode == "static": climb current_env.parent links (ignore call_stack).
    mode == "dynamic": search call_stack from most-recent (index -1)
        to oldest (index 0), checking each caller's OWN locally-defined
        names only (not their parents), falling back to the global
        (outermost lexical) environment if not found on the stack.
    Any other mode raises ValueError. Raise SemanticError if `name`
    cannot be resolved under the requested mode.
    """
    if mode not in ("static", "dynamic"):
        raise ValueError(f"Invalid mode {mode!r}: expected 'static' or 'dynamic'.")

    if mode == "static":
        return current_env.resolve(name)

    # mode == "dynamic": most-recent caller first, checking only each
    # caller's own locally-defined names (not their lexical parents).
    for caller in reversed(call_stack):
        if name in caller._names:
            return caller._names[name]

    # Fall back to the outermost (global) lexical environment.
    global_env = current_env
    while global_env.parent is not None:
        global_env = global_env.parent
    if name in global_env._names:
        return global_env._names[name]

    raise SemanticError(f"Use of undeclared variable '{name}' (dynamic mode).")
