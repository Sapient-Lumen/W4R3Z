# Project identity and boundaries

Revision: rev0028

## Identity

BrowserRT is a runtime kernel for browser-resident software. The kernel owns
coordination, not domain semantics.

Its natural clients are future libraries like local analytics engines, video
pipelines, giant canvas/vector engines, browser IDEs, local-first databases,
AI-agent artifact workbenches, and testing harnesses. BrowserRT should make
those clients faster to build because the hard runtime substrate is already
specified and tested.

## Kernel nouns

BrowserRT should keep a small vocabulary and force every future feature through
it:

| Noun | Meaning |
|---|---|
| task | Bounded unit of work with priority, lane, deadline, signal, trace id. |
| agent | Lifecycle-managed worker-like participant. |
| supervisor | Owner that reconciles desired agent/task state after failure. |
| object ref | Handle to data-plane bytes, stream, OPFS block, shared slab, or GPU buffer. |
| lane | Resource class such as CPU, storage, GPU, render, media, mesh, or maintenance. |
| provider | Concrete implementation behind a lane. |
| trace | Runtime evidence stream for debugging, timing, replay, and claims. |
| manifest task | Scheduleable test/proof slice with cost, risk, capabilities, and outputs. |

## Boundary rule

BrowserRT may contain primitive providers and adapters. It should not contain
application policy that belongs one layer above.

Examples:

- BrowserRT may provide an OPFS block store; a database owns tables and indexes.
- BrowserRT may provide GPU dispatch; a charting engine owns chart semantics.
- BrowserRT may provide render lanes; a vector editor owns scene semantics.
- BrowserRT may provide WebCodecs/media scheduling later; an editor owns timeline semantics.
- BrowserRT may provide plugin capability accounting; an app owns plugin marketplace policy.

## Shape of success

A successful BrowserRT does not make every app use the same UI or data model. It
makes every serious browser app stop re-solving the same runtime problems:

- how to keep main-thread jank bounded,
- how to avoid cloning giant payloads,
- how to recover after worker failure,
- how to preserve storage integrity,
- how to test browser-only features in a short cloudtainer turn,
- how to know which fallback path ran,
- how to reproduce a failure with a trace.

## Shape of failure

The project fails if it becomes any of these:

- a worker-pool convenience wrapper,
- a pile of unconnected browser probes,
- a giant integration test that cannot fit inside a turn,
- a collection of ambition docs without executable proof,
- a performance-claim machine without real external hardware evidence,
- a framework-specific runtime,
- a monolith that apps cannot selectively adopt.

## The irreversible design pressure

Every layer must be decomposable. Every proof must be sliceable. Every expensive
claim must have a trace. Every future feature must have a fallback or a declared
non-claim. That is the only way the cube can grow without becoming impossible to
validate in a cloudtainer.
