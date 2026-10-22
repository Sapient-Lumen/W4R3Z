# Schell

[SlopOS](../README.md) · [Complete editions](../DOWNLOADS.md#schell)

## Command work with a life story

Schell imagines a command line in which work becomes easier to navigate because its meaning survives. A command would have more than a string and an exit code: it would have an author, an execution context, an account of its effects, and a relationship to what happened before and after. Within OG 510P's SlopOS constellation, Schell is the temporal instrument: the place where action becomes an inspectable episode and useful memory.

Its smallest proposed win is deliberately ordinary. Select one exact document, ask to open or send it, inspect the narrow access request and its expiry, approve or deny, and receive a durable receipt. Starting with one artifact makes the interaction comprehensible before a whole shell language must be settled. The point is not another elaborate command syntax. It is a better relationship between selecting something, authorizing an action, and understanding the result. [Read the founding open/send RFC](../sources/Schell/rev0270/rfcs/0005-smallest-obvious-win-open-send.md).

## Four cards, four kinds of confidence

Imagine a terminal that presents a completed command as a chapter card. A direct launch with exact arguments and captured output can be quiet: the facts are close at hand. Open its evidence drawer and find what ran, who supplied the semantic marks, where the facts hold, which output bytes are covered, what the next action would spend, and where the raw receipt lives.

Now imagine restoring a successful remote command from last week. Its familiar path also exists in your local checkout. Schell's proposed card keeps the old work useful without silently choosing which machine or object you meant. Its next verbs are choose route, attach read-only, refresh, or recall to draft. Rerunning is a new request grounded in the present, not an effect smuggled out of memory.

Two further cards test less comfortable situations. A program prints fake prompt marks, a misleading hyperlink, or a clipboard escape; useful output remains visible, but the program cannot declare its own output trusted shell truth. A helper performs or proposes a batch of work; its identity, policy context, sandbox, and individual effects remain inspectable rather than disappearing beneath fluent prose. These four situations form a compact design object, with six evidence rows behind each card. [Read the four-card prototype](../sources/Schell/rev0270/docs/80-terminal/four-card-downgrade-literacy-prototype-and-evidence-dockets.md).

The paper rendering makes an unusually specific artistic choice: a compact header, at most three quiet chips and three warning chips, then a docket drawer. Prefer actionable verbs to a wall of cautions. Strong evidence should allow the interface to be calm; weak evidence should change what can honestly be offered. The archive calls these paper prototypes, not product UI. [See the rendered cards and replay capsules](../sources/Schell/rev0270/docs/80-terminal/rendered-four-card-glance-prototype-and-replay-capsules.md).

## Beauty that survives the terminal

Schell separates action meaning from presentation. The shell would own identities and lineage; semantic transport would preserve their boundaries; the terminal could supply local visual luxury. A plain transcript still needs to say where review, denial, receipt, output, and background change occurred. Otherwise the beautiful version would hold the truth hostage whenever someone used SSH, exported a log, or switched renderers. [Read the transcript contract](../sources/Schell/rev0270/docs/80-terminal/transcript-truth-and-zone-persistence.md).

Memory consequently becomes more than a history palette. A remembered chapter may travel into a search index, an assistant's context, a shared issue, or an exported artifact. Removing the visible original cannot establish that all those copies or influences disappeared. The later retention work explores a two-tier presentation: a concise glance line, with more detail required before consequential reuse. Its prediction exercise is explicitly synthetic maintainer self-review, not an independent usability study. The recorded misreads are questions for future operators, not measurements of how people actually performed. [Inspect the retention prediction exercise](../sources/Schell/rev0270/docs/80-terminal/retention-forgetting-prediction-run-v0.json).

## The work present in rev0270

The supplied edition contains Python tools and structured specimens rather than the proposed Rust shell or a working terminal renderer. Some tools check fixture shape and coverage. Others implement narrower file mechanisms: the release builder constructs a sorted, uncompressed ZIP with fixed timestamps and controlled metadata. [Read the package builder](../sources/Schell/rev0270/tools/build_release_package.py).

Its paired verifier checks the expected file set, ordering, archive metadata, sizes, modes, and SHA-256 content against manifest entries. These are tangible custody tools in source form; they do not execute command chapters or establish a policy runtime. [Read the package verifier](../sources/Schell/rev0270/tools/verify_deterministic_package.py).

Schell's strongest idea is that command work can become richly object-like without losing the plain account underneath. It offers a speculative terminal culture in which remembering, explaining, sharing, and doing remain related pleasures, but never become interchangeable acts.
