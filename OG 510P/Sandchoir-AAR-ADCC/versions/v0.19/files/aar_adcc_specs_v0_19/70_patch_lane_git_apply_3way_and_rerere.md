# 70 — Patch Lane: git apply --3way + rerere (v0.19)

You want agents to collaborate on the same repo without stepping on each other.
The lowest-hanging fruit is: **patch-shaped exports + integrator applies**.

This doc defines a robust default patch-application pipeline using git features.

## 1) Patch export format
Preferred:
- `git diff` from agent worktree branch → store as P# in ledger
Also allow:
- unified diff file

P# includes:
- summary (<= 5 lines)
- touched files list
- verifier intent (what should pass)
- base ref (commit hash) if available

## 2) Apply pipeline (integrator)
1) ensure canonical worktree clean
2) attempt apply:
   - `git apply --3way --index <patch>` (3-way if blob IDs present)
3) if conflicts:
   - leave markers; resolve manually or by small follow-up patch
4) run cheap verifiers (typecheck_fast/unit_fast)

## 3) Rerere to reduce repeated conflicts
Enable rerere:
- `git config rerere.enabled true`
Once you resolve a conflict once, rerere can reuse it next time.

## 4) Where this fits the protocol
- Integrator owns application, not authorship.
- Agents propose patches; integrator applies (or requests changes).
- Evidence moves votes: patches without checks are lower priority in Gatekeeper.

## 5) Failure handling
- If patch cannot be applied: mark P# as “stale” and request rebase/export again.
- Prefer smaller patches to reduce conflict surface.
