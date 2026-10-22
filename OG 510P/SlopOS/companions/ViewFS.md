# ViewFS

[SlopOS](../README.md) · [Complete editions](../DOWNLOADS.md#viewfs)

## A filesystem organized around relationships

ViewFS asks what working with files could feel like if each application saw a deliberately assembled world. Instead of beginning with a new disk format, it begins with immutable objects, explicit-rights handles, per-process views, and mediated import and export. A path becomes a useful way to navigate that world, not the source of every power inside it. Within OG 510P's SlopOS constellation, ViewFS supplies an object-and-access imagination that reaches from storage into the shell.

The founding slice is intentionally comprehensible: store objects, hold bounded handles, bind those handles into a view, and let familiar path-based tools operate through a compatibility membrane. Decisions about the final storage format, replication, mutable transactions, and shell syntax remain open. That ordering makes the project more interesting than a proposed replacement for an existing filesystem: it asks which relationships should be native before deciding how their bytes should be packed. [Read the foundation RFC](../sources/ViewFS/rev0176/rfcs/0001-viewfs-foundation-rfc.md).

## Bringing a document into a workspace

Imagine choosing an outside document for an application. In ViewFS's intended workflow, a portal mediates the selection and produces bounded access. That handle is explicitly bound into the application's view. The document can then appear at a convenient path, while its identity, its placement, and the rights currently held remain separate facts.

The latest core schema supplies names for those differences. An `ObjCore` names committed identity. An `ObjRef` can remember or describe it. A `Handle` carries current rights, while a `ViewRoot` assembles explicit bindings for a process. A receipt records what happened without reopening the document later. This gives the imagined user a powerful combination: durable memory of work without the assumption that remembering an object must preserve access to it forever. [Read the core schema](../sources/ViewFS/rev0176/docs/30-architecture/core-schema-v0.md).

The same distinction matters when search or an assistant enters the workflow. A result, summary, or retrieved excerpt can help select a document; its text is not itself permission to read the source or execute a plan. Derived copies also have their own lifecycle. Deleting the source is not an adequate account of an embedding, cached answer, thumbnail, or exported copy. ViewFS tries to make that distributed residue describable rather than hiding it behind one optimistic deletion state.

## The shell as a changing instrument

One of the archive's most vivid pieces follows a line of input through six proposed appearances: editable buffer, parse lens, diagnostic rail, bound packet gutter, prepared-action shutter, and historical receipt ghost. The progression gives editing, analysis, routing, review, and memory different visual forms.

While you type an incomplete command, “recovery fog” could show where the parser is guessing. A diagnostic rail would distinguish syntax feedback from lint, policy advice, and old history. After binding, a packet gutter could name the current pane's handle and indicate whether a portal or rebind is needed. Identical text might compile differently when those live bindings change, and a comparison card would explain why. [Explore parse lenses and packet gutters](../sources/ViewFS/rev0176/docs/70-shell/parse-lenses-diagnostic-rails-and-packet-gutters.md).

This is ViewFS's artistic contribution: giving an invisible change in relationship a visible texture. It is a design for a rich shell, not a claim that the shell exists already. The desired pleasure is immediate structure and navigability, with uncertainty presented as something one can work with rather than a red-or-green verdict.

## Meeting ordinary tools

The latest host-adapter design takes familiar filesystem expectations seriously: mounts, stat-like metadata, inode aliases, watches, locks, rename plans, temporary files, hydration, and external-app handoff. It treats these as projections over current access, not replacements for it. [Read the compatibility design](../sources/ViewFS/rev0176/docs/30-architecture/host-adapter-compatibility-v0.md).

Its proposed cards show the provider, policy epoch, sandbox fit, backing handle, and whether state is current, advisory, stale, or historical. A watcher can report a change without giving its recipient access. An “open with” handoff can identify the receiver and receipt without silently creating permanent delegation. These details make compatibility feel like a legible relationship rather than a hidden escape hatch. [Read the host-adapter cards](../sources/ViewFS/rev0176/docs/70-shell/host-adapter-stat-watch-handoff-cards.md).

## A model with explicit verdicts

Rev0176 includes a Python checker that evaluates operations over supplied JSON records. Its mount evaluator rejects stale policy, unsuitable sandbox state, root-authority claims, or missing live mount rights. Its stat evaluator checks requested fields and backing access. These are implemented model decisions, not actual mounts or host measurements: even a fixture labeled `fuse` does not supply a FUSE backend. [Inspect the core checker](../sources/ViewFS/rev0176/tools/check_viewfs_core_fixtures.py).

The companion intake documents how SlopOS and sibling ideas become local schema and fixture pressure, not a claim of whole-system integration. [Read the companion intake](../sources/ViewFS/rev0176/docs/30-architecture/companion-seam-intake.md). ViewFS's distinctive promise is a computer whose views can be welcoming and familiar while the relationships beneath them remain exact enough to inspect, narrow, repair, and eventually implement.
