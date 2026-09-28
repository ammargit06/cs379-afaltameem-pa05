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
    # TODO
    raise NotImplementedError
