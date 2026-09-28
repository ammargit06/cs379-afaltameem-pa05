# PA 5 Theory: The Scope Resolver

## 1. Static vs. Dynamic Scoping (15 pts)

**Static (lexical) scoping** resolves a free variable by looking at *where the reference sits in the source text*. A name is bound to whichever declaration textually encloses it, found by walking outward through the nesting of blocks/functions as they appear on the page — exactly what `Environment.parent` encodes: each scope points to the scope it is lexically written inside of, and that chain never changes once the program is written.

**Dynamic scoping** resolves a free variable by looking at *who is currently calling whom at run time*. Instead of climbing lexical parents, it walks the call stack backward from the currently executing procedure through its caller, its caller's caller, and so on, using whichever binding it finds first on that stack. The same line of code can therefore resolve a name differently on different calls, depending on who happened to call it.

**Python uses static scoping** (a name inside a function resolves against the enclosing function/module text, per the LEGB rule, regardless of who calls it). **Bash uses dynamic scoping** for shell variables absent `local` — a function that references a variable it never declared picks up whatever value is currently set in the caller's environment at the moment it runs, not whatever was textually around it when it was defined.

**Why static scoping is more predictable at scale:** under static scoping, the binding of a free variable is a fixed property of *where the code lives on disk*. Given only the source file (and the files it lexically nests inside/imports into scope), you can determine, without ever running the program, exactly which declaration a name refers to — because that declaration is fixed by nesting structure the moment the code is written, and callers have no way to change it. Under dynamic scoping, the same free-variable reference could resolve to a different binding on every single invocation, depending on the full chain of callers that happened to be active at run time. For hundreds of files maintained by a large team, that means a static-scoping bug is local — you can find and fix a wrong binding by reading the one file where the reference and its enclosing declarations live — while a dynamic-scoping bug requires reconstructing the entire call history at the moment of failure, which may involve code in files the reader has never seen and that the original author never anticipated as a possible caller.

## 2. The Classic Divergence, Traced (15 pts)

```
global x = 10        (line 1)

proc A():
    local x = 1       (line 2)
    call B()

proc B():
    print(x)
```

**(1) Lexical nesting diagram (what static scoping uses):**

`B` is *written* at global scope, so its lexical parent is the global scope — `A`'s body is not part of `B`'s lexical nesting at all, regardless of who calls `B`.

```
Global scope  { x = 10 }  (line 1)
   |-- parent of --> A's scope  { x = 1 }   (line 2)
   |-- parent of --> B's scope  { }         (no locals; parent = Global)
```

**(2) Call stack diagram (what dynamic scoping uses):**

At the moment `B` executes, the stack reflects *who called whom*, not how the code is nested on the page.

```
call stack (oldest -> newest):
[ Global ]  ->  [ A: x = 1 ]  ->  [ B: (running) ]
                    ^
                    most recent caller checked first
```

**Values printed:**
- **Static scoping** climbs `B`'s lexical parent chain (`B -> Global`), skipping `A` entirely since `A` is not `B`'s lexical parent. It finds `x` in the global scope and prints **`10`** (declaration line 1).
- **Dynamic scoping** walks the call stack from the most recent caller backward: `A` is the active caller and it defines a local `x`, so the search stops there and prints **`1`** (declaration line 2), never reaching the global `x`.

These genuinely diverge: **10 vs. 1**, both for the identical reference `print(x)` inside `B`, purely because the two mechanisms consult different structures (lexical nesting vs. run-time call history) to resolve the same free name.

## 3. Scope Holes (10 pts)

A **scope hole** is a region of code where a name is technically still "in scope" by lexical nesting — an outer declaration of that name exists and would ordinarily be reachable by climbing the parent chain — but a *closer* declaration of the identical name (usually a parameter or a local variable in an inner, nested function) shadows it for the entire body of that inner scope. Inside the hole, every reference to the name resolves to the inner declaration; the outer one is syntactically unreachable there, even though nothing has removed it from scope — it is simply never checked because lookup stops at the first match.

**Example:**

```
global total = 100        (line 1)

func apply_discount(total):     # parameter also named `total` (line 2)
    total = total * 0.9         # this `total` is ALWAYS the parameter
    print(total)                 # scope hole: the outer `total` (line 1)
                                  # is unreachable for the rest of this body
```

From line 2 to the end of `apply_discount`'s body, every unqualified reference to `total` resolves to the parameter, because lexical lookup finds it in the function's own scope before ever climbing to the global scope. The global `total = 100` is still "in scope" in the sense that it exists and the parent pointer to it is intact — but it has become a scope hole: there is no way to name it from inside this function body without an extra mechanism (e.g., an explicit `global` qualifier), because ordinary lookup always finds the nearer binding first.

## 4. Dynamic Scoping and Shared State (10 pts)

Dynamic scoping's lookup mechanism *is* the call stack — resolving a free variable means reading frames off a stack that is simultaneously being mutated by every call and return happening in the program. The shared piece of state at risk is exactly that: **the call stack itself**, treated as a live, shared, mutable structure that name resolution reads through while other execution is writing to it.

In a concurrent or multithreaded interpreter, if two threads push and pop frames on a call stack that a dynamic name resolution is walking at the same time, several things can go wrong:

- **Torn reads / inconsistent frames** — the resolver could observe a stack that is mid-mutation: a frame partially pushed, or a frame popped out from under the resolver's current position, producing a resolution against a caller environment that no longer represents any real, still-executing call.
- **Wrong-thread bindings** — if the call stack is shared rather than per-thread, a resolution running on behalf of thread A could walk frames pushed by thread B's completely unrelated call chain, binding a free variable to a value that has nothing to do with the logical caller sequence of the code actually asking for it.
- **Race-induced crashes or corruption** — concurrent push/pop against the same underlying list/array without synchronization can corrupt the stack's internal structure (lost updates, out-of-bounds indices, or the classic lost/duplicated element bugs of unsynchronized concurrent stacks), causing the resolver to crash or silently read garbage instead of raising a clean error.

None of this is a problem for static scoping, since its lookup structure (the lexical `parent` chain) is fixed at parse/definition time and never mutated during execution — there is nothing for a second thread to be concurrently changing. Dynamic scoping's hazard is specifically that its "source of truth" is also the most actively-mutated piece of run-time state in the entire interpreter.
