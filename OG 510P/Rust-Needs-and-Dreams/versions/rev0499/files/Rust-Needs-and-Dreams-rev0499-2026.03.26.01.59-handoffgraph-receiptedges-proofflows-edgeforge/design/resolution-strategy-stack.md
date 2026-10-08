# Design: Resolution Strategy Stack

## Why this stack exists
The archive already has a meaningful **Dependency Control Stack**:
- [`design/resolution-doctor-kit.md`](./resolution-doctor-kit.md)
- [`design/feature-kit.md`](./feature-kit.md)
- [`design/dependency-control-stack.md`](./dependency-control-stack.md)

That stack explains:
- what Cargo selected,
- why features activated,
- where unification happened,
- and what downstream consumers might import next.

What it still under-specifies is the layer above those facts:
- **what objective was being pursued,**
- **which tradeoffs were acceptable,**
- **which alternatives mattered,**
- and **which consumer was the real audience** for this selection.

That is now important because Rust’s resolution story is no longer one-dimensional.
MSRV-aware resolution is real, minimal-version checks remain real, publish-time-aware resolution is emerging, and downstream semver/policy/migration work increasingly depends on accurate resolution provenance.

## The stack
### 1) Dependency Control Stack
Owns:
- chosen graph truth
- feature activation and unification truth
- conflict and reproducer truth

Question:
> what graph did Cargo choose, and why are these capabilities active?

### 2) Resolution Strategy Kit
Owns:
- objective profiles
- accepted tradeoffs
- bounded candidate / alternative summaries
- strategy diffs
- consumer handoff posture

Question:
> what sort of resolution were we trying to obtain, what alternatives mattered, and why was this outcome acceptable?

### 3) Downstream consumers
Should import, not overwrite, strategy truth:
- **Migration Truth Stack**
- **Public API Kit / Package Admission Stack**
- **Policy / Trust**
- **Support Envelope / Compatibility Claims**
- **Release / Distribution / Incident consumers**

Question:
> given the chosen strategy, what may this consumer conclude or review next?

## Working thesis
A worthy contribution here should let a reviewer answer all of these without reading CI shell history:
1. What objective profile was active?
2. Which config / workspace / manifest / toolchain posture shaped it?
3. What graph and features were actually selected?
4. What alternative strategies were examined or deliberately not examined?
5. Which tradeoffs were accepted?
6. Which downstream consumer may safely import the result?
7. Which uncertainty came from Cargo heuristics, incomplete registry history, or candidate exploration limits?

If the stack cannot answer those questions, it is not yet ecosystem infrastructure.

## Design rules
1. **Dependency Control remains factual.** Do not let strategy artifacts silently replace chosen-graph truth.
2. **Strategy is not policy.** “We targeted MSRV fallback” is not the same as “policy approved this result”.
3. **Strategy is not migration.** A migration may import one or more strategy reports, but it still owns the broader source→destination program.
4. **Named profiles beat folklore.** `latest`, `direct-minimal-check`, `msrv-fallback`, `publish-time`, and later bounded profiles are better than prose like “normal resolution but safer”.
5. **Inconclusive is allowed.** Candidate comparison and time-travel/history-aware resolution can be partial.
6. **Historical posture must be explicit.** Publish-time and release-age objectives must say what registry history was actually visible, what yanks or mirrors may have been missing, and what was only approximated.
7. **Lockfile outcomes are not enough.** The stack must keep the distinction between lockfile generation posture, compile-time feature posture, and downstream consumer interpretation.

## Recommended execution posture
The next credible move is a ranked pilot program captured in:
- [`design/resolution-strategy-pilot-program.md`](./resolution-strategy-pilot-program.md)

That rollout should prove the stack in the following order:
1. direct-vs-minimal validation lane
2. workspace multi-MSRV lane
3. publish-time / release-age lane
4. release-admission / semver handoff lane
5. migration / support / policy consumer lane

## Anti-goals
Do not turn this stack into:
- one solver replacement,
- one global dependency policy engine,
- one giant lockfile dashboard,
- or one false promise that all “best graph” questions have a universal answer.

The stack is a **review boundary for strategy**, not a new package manager.
