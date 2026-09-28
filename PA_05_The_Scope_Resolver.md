# PA 5: The Scope Resolver
## CS 379: Programming Languages (Fall 2026)

### 🔧 Pipeline Context
This is **Stage 5 of the USILang interpreter pipeline**. You consume the `Environment` class from PA 4 — its `parent`-pointer chain already encodes *lexical* (static) structure — and you extend it with a second, configurable lookup strategy so the same name resolution machinery can behave either **statically** or **dynamically**. You produce the scope-resolved environment model that PA 6 will build on: next week's activation records need to know, for every variable reference, exactly which mechanism decided where that variable lives, because that decision determines what a "stack frame" even has to store.

USILang's grammar doesn't yet have function *syntax* — that's introduced alongside activation records in PA 6. So this week you'll work one level below the syntax: you'll resolve names against `Environment` objects and a **call stack** that the provided test harness constructs directly, simulating what happens when one procedure calls another. This isolates the pure scoping *mechanism* — the part Sebesta Sections 5.5–5.6 are actually about — from the parsing machinery you'll wire it into next week.

---

### Part A: The Specification (50 Points)
**Instructions:** Answer the following questions in a separate document (PDF or Markdown).

1. **Static vs. Dynamic Scoping (15 pts):**
   Define static (lexical) scoping and dynamic scoping in your own words. State which one Python uses and which one Bash uses (for its shell variables absent `local`). Then justify: for a codebase with hundreds of files written by a large team, why is static scoping considered dramatically more predictable to reason about than dynamic scoping — specifically, what can you determine about a free variable's binding under static scoping just by reading source code, that you cannot determine under dynamic scoping without also knowing the full call history at run time?

2. **The Classic Divergence, Traced (15 pts):**
   Consider this pseudocode (not valid USILang syntax yet — just a scoping thought experiment):
   ```
   global x = 10

   proc A():
       local x = 1
       call B()

   proc B():
       print(x)
   ```
   `B` is declared at global scope (so its lexical parent is the global scope, where `x = 10`), but `B` is *called* from inside `A`, where a different, local `x = 1` is in effect. Draw two diagrams: (1) the **lexical nesting** diagram static scoping uses to resolve `x` inside `B`, and (2) the **call stack** dynamic scoping uses instead. State the value each strategy prints for `x`, and confirm they genuinely diverge.

3. **Scope Holes (10 pts):**
   Define a "scope hole" in the context of static scoping with nested functions and name shadowing. Construct a short example (pseudocode is fine) where an inner function's parameter name shadows an outer variable of the same name, creating a scope hole for the rest of the inner function's body — i.e., a region of code where the outer name is syntactically unreachable even though it's still "in scope" by nesting.

4. **Dynamic Scoping and Shared State (10 pts):**
   Dynamic scoping resolves a free variable by walking the **call stack** at run time rather than the lexical source structure. Explain why this makes dynamic scoping specifically dangerous in a concurrent or multi-threaded interpreter: what shared piece of state is at risk, and what could go wrong if two threads were simultaneously pushing and popping call-stack frames that a dynamic name resolution was walking through? (You don't need to solve this — just diagnose the hazard. We'll return to synchronization in Week 11.)

---

### Part B: The Implementation (50 Points)
**Instructions:** Implement a configurable scope resolver in a file named `scope_resolver.py`, extending (by importing, not copy-pasting) the `Environment` class from PA 4's `symtable.py`.

**Required interface:**
```python
def resolve_name(
    name: str,
    current_env: Environment,
    call_stack: list[Environment],
    mode: str,          # "static" or "dynamic"
) -> int:                # returns the declaration line of the resolved binding
    ...
```

**Requirements:**
1. **Mode validation** — `mode` must be exactly `"static"` or `"dynamic"`; any other value raises `ValueError`.
2. **Static mode** — ignore `call_stack` entirely. Resolve `name` by climbing `current_env.parent` links exactly as PA 4's `Environment.resolve` does (you may call it directly). Raise `SemanticError` if not found anywhere in the lexical chain.
3. **Dynamic mode** — ignore `current_env.parent` (except as the final fallback to the outermost/global scope). Instead, search `call_stack` **from the most recently pushed caller environment backward toward the oldest**, checking each caller's own locally-defined names (not their lexical parents) for `name`. If no caller on the stack defines it, fall back to the global environment. Raise `SemanticError` if still not found.
4. **The call stack is a list of `Environment` objects representing callers**, pushed in call order (index `0` is the oldest/outermost caller, index `-1` is the most recent). Your dynamic search must iterate it in the correct order — most recent first — to match how a real runtime call stack unwinds.
5. **Divergence correctness** — given the classic example from Part A, Question 2 (constructed for you by the test harness as real `Environment`/call-stack objects, not USILang source), `resolve_name(..., mode="static")` must resolve `x` to the **global** declaration, and `resolve_name(..., mode="dynamic")` must resolve `x` to **`A`'s local** declaration — the two modes must produce genuinely different declaration lines for the identical inputs except for `mode`.
6. **Verification:** Run
   ```
   python test_scope_resolver.py
   ```
   The harness builds the lexical `Environment` chain and the call stack for several scenarios, including the classic divergence case, and checks: (a) static mode always matches a reference lexical-only resolver, (b) dynamic mode always matches a reference call-stack-only resolver, and (c) the divergence case produces two different, specifically-expected line numbers under the two modes. If every case matches, it prints the **Success Token**.

### What Success Looks Like

Your resolver should make the lookup structure observable:

- In the classic divergence case, static lookup returns declaration line `1` from the global lexical parent, while dynamic lookup returns declaration line `2` from the newest caller frame.
- When no caller defines a name, dynamic lookup falls back to the global environment.
- A missing name raises `SemanticError` in both modes, and any mode other than exactly `"static"` or `"dynamic"` raises `ValueError`.

A complete harness run ends with output in this form:

```text
[PASS] static mode resolves B's free 'x' to the GLOBAL declaration (line 1)
[PASS] dynamic mode resolves B's free 'x' to A's LOCAL declaration (line 2)
[PASS] dynamic mode falls back to the global environment
[PASS] dynamic mode raises SemanticError for an unresolvable name
============================================================
  ALL CHECKS PASSED -- PA05
  STUDENT: your_username
  SUCCESS TOKEN (paste this into Blackboard):
  <your student-specific token>
============================================================
```

---

### 🚀 Submission
1. `PA5_Theory.pdf` (or `.md`) — your Part A answers.
2. `scope_resolver.py` — your completed configurable scope resolver.
3. The **Success Token** generated by `test_scope_resolver.py`.

Keep your completed `lexer.py`, `parser.py`, and `symtable.py` in the repository so the import chain works, but submit only the three items listed above to Blackboard.
