"""
PA 5: The Scope Resolver -- verification suite.

Run: python test_scope_resolver.py
Prints the Success Token only if every check below passes.
"""

import base64
import hashlib
import sys

from scope_resolver import resolve_name
from symtable import Environment, SemanticError

ASSIGNMENT_ID = "PA05"


def get_student_id() -> str:
    """Prompt for the student's USI username; baked into the Success Token
    so a copied/shared token decodes to someone else's name, not yours."""
    student_id = input("Enter your USI username (e.g. cwill): ").strip()
    while not student_id:
        student_id = input("Username cannot be blank. Enter your USI username: ").strip()
    return student_id


def generate_token(assignment_id: str, student_id: str) -> str:
    digest = hashlib.sha256(f"CS379-{assignment_id}-{student_id}-VERIFIED".encode()).hexdigest()[:16]
    raw = f"CS379|{assignment_id}|{student_id}|PASS|{digest}"
    return base64.b64encode(raw.encode()).decode()


def print_success_banner(assignment_id: str) -> None:
    student_id = get_student_id()
    token = generate_token(assignment_id, student_id)
    print("\n" + "=" * 60)
    print(f"  ALL CHECKS PASSED -- {assignment_id}")
    print(f"  STUDENT: {student_id}")
    print("  SUCCESS TOKEN (paste this into Blackboard):")
    print(f"  {token}")
    print("=" * 60 + "\n")


def check(label: str, condition: bool, failures: list) -> None:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {label}")
    if not condition:
        failures.append(label)


def main() -> int:
    failures: list = []

    print("Testing mode validation...\n")
    global_env = Environment()
    global_env.define("x", 1)
    try:
        resolve_name("x", global_env, [], mode="sideways")
        check("an invalid mode string raises ValueError", False, failures)
    except ValueError:
        check("an invalid mode string raises ValueError", True, failures)

    print("\nTesting static mode (lexical chain only)...\n")
    parent = Environment()
    parent.define("y", 5)
    child = Environment(parent=parent)
    child.define("z", 6)
    check("static mode finds a name in the current scope", resolve_name("z", child, [], mode="static") == 6, failures)
    check("static mode climbs to the lexical parent", resolve_name("y", child, [], mode="static") == 5, failures)
    try:
        resolve_name("nope", child, [], mode="static")
        check("static mode raises SemanticError for an unresolvable name", False, failures)
    except SemanticError:
        check("static mode raises SemanticError for an unresolvable name", True, failures)

    print("\nTesting dynamic mode (call stack, most-recent-first)...\n")
    caller_old = Environment()
    caller_old.define("w", 10)
    caller_old.define("v", 15)   # only the OLDER caller defines v
    caller_new = Environment()
    caller_new.define("w", 20)  # both callers define w -- newest must win
    isolated_current = Environment()  # the callee's own (empty) local scope
    check(
        "dynamic mode checks the MOST RECENT caller (index -1) first",
        resolve_name("w", isolated_current, [caller_old, caller_new], mode="dynamic") == 20,
        failures,
    )
    check(
        "dynamic mode falls back through older callers if the newest doesn't define it",
        resolve_name("v", isolated_current, [caller_old, caller_new], mode="dynamic") == 15,
        failures,
    )

    global_fallback = Environment()
    global_fallback.define("g", 30)
    callee = Environment(parent=global_fallback)
    check(
        "dynamic mode falls back to the global environment",
        resolve_name("g", callee, [caller_old, caller_new], mode="dynamic") == 30,
        failures,
    )
    try:
        resolve_name("nope", callee, [caller_old, caller_new], mode="dynamic")
        check("dynamic mode raises SemanticError for an unresolvable name", False, failures)
    except SemanticError:
        check("dynamic mode raises SemanticError for an unresolvable name", True, failures)

    print("\nReplaying the Part A, Question 2 classic divergence case...\n")
    # global x = 10 (line 1)
    # proc A(): local x = 1 (line 2); call B()
    # proc B(): print(x)
    global_scope = Environment()
    global_scope.define("x", 1)  # global x, declared line 1

    a_scope = Environment(parent=global_scope)
    a_scope.define("x", 2)  # A's local x, declared line 2

    b_scope = Environment(parent=global_scope)  # B is lexically declared at global scope
    call_stack_during_b = [a_scope]  # A called B, so A is the active caller on the stack

    static_result = resolve_name("x", b_scope, call_stack_during_b, mode="static")
    dynamic_result = resolve_name("x", b_scope, call_stack_during_b, mode="dynamic")

    check("static mode resolves B's free 'x' to the GLOBAL declaration (line 1)", static_result == 1, failures)
    check("dynamic mode resolves B's free 'x' to A's LOCAL declaration (line 2)", dynamic_result == 2, failures)
    check("static and dynamic modes genuinely diverge on the same inputs", static_result != dynamic_result, failures)

    print()
    if failures:
        print(f"{len(failures)} check(s) failed. No token issued.")
        return 1

    print_success_banner(ASSIGNMENT_ID)
    return 0


if __name__ == "__main__":
    sys.exit(main())
