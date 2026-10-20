# qomrade

## Let a project keep developing, not merely a prompt keep repeating

qomrade is a browser-side continuation tool for sustained work in ChatGPT. A research collection can acquire better sources and sharper exclusions; an argument can encounter objections and change; a translation can revisit its lexical decisions; a software project can be inspected, built, revised and delivered again. qomrade keeps supplying the next occasion to work without requiring someone to send every continuation by hand.

Its central arrangement is simple but consequential: **the instruction can stay the same while the project changes**. A request to continue useful work refers to the current conversation, current materials and current state of the inquiry. The next turn need not repeat the previous answer. It can act on what that answer discovered, what a test rejected, or what the latest artifact now makes possible.

[Open the complete qomrade 0.18.40 source](../Maintained%20Tools/qomrade.user.js), including its runtime contract and embedded development workbench.

## The work supplies the changing subject

A useful continuation begins with an established project: its aim, materials, current questions and the permissions under which it may proceed. For example, a research collection might ask each turn to read a promising source, distinguish its findings from inference, revise the collection where warranted and preserve the next useful question. Some turns might add an essay. Others might reject an attractive claim or discover that the existing account should remain unchanged.

The same arrangement can support software construction. A turn inspects the present project, chooses a warranted change, carries out the available checks, and leaves a complete successor with enough orientation for another turn. Prose, rejected approaches and negative results can be construction materials alongside source code: they prevent the next turn from repeatedly rediscovering why an apparently easy path was abandoned.

qomrade supplies recurrence, not the research judgment, compiler or project itself. Those come from the model, its available tools and the materials carried forward. This separation is what makes the arrangement adaptable. The browser controller need not understand every new research question or acquire a new workflow for every descendant program. It can continue issuing the operator's instruction while the project becomes more capable and more particular.

The [OG 510P collection](../OG%20510P/README.md) offers substantial examples of the kind of cumulative work at stake: stories and retellings, philosophical inquiry, translation and systems research. They are works to read in their own right, not interchangeable outputs or a provenance claim that one qomrade revision produced every snapshot.

## A continuation is a witnessed transaction

The controller does more than press a button periodically. At **Start**, it captures the operator's prompt for that run; subsequent editor changes do not silently replace it. Before each Send it obtains fresh evidence for the selected model policy, inserts and reads back the prompt, checks the conversation and generation state, and checks again at the final click. If a matching user turn has already appeared during insertion, it can adopt that turn rather than duplicate the Send. The [send path](../Maintained%20Tools/qomrade.user.js#L8078-L8275) makes the difference between intending to send, clicking Send and observing an accepted user turn explicit.

A reply is not accepted merely because some text appeared. The controller waits for a new assistant turn after the owned request, no active generation, stable text and no unresolved structural tool-only work. This lets a long turn remain a long turn instead of treating an intermediate work display as the finished answer. The configurable gap defaults to 30 minutes; cadence is enforced again after asynchronous model and composer work rather than assuming that an earlier check still holds.

There are three model policies. **Smart Pro** in this supplied revision prefers the explicit GPT-5.6 Pro route and bounds its GPT-6-or-newer fallback to the relevant failure or unavailable-route situation. Stable success restores the ordinary preference. **Pin** selects a particular discovered route and effort without silent fallback. **Follow** witnesses the current selection without changing it. These are live website-control choices, not evidence about the identity of a backend model. See the [runtime contract](../Maintained%20Tools/qomrade.user.js#L189-L241).

The controller also distinguishes a recoverable failure from a completed conversation. Its current-request recovery sends a fresh copy of the captured prompt after the required evidence and backoff; it does not press native Retry. A conversation-length barrier ends the run. Optional Safe refresh addresses separately bounded page-maintenance situations, not a general license to reload a slow request. A fresh message can repeat work whose backend fate is unknown, so project-side receipts and checks remain valuable when the work has consequential effects.

## Carry the work, and distinguish the kinds of handoff

A continuation tool and a portable project solve different parts of the same practical problem. The former supplies another turn; the latter gives that turn something durable and intelligible to inherit. [DelayBasin](../OG%20510P/DelayBasin/README.md) makes the distinction sharper: a store of evidence, a compact re-entry packet and checks for accepting a revision do not do the same job. Keeping everything is not automatically the best way to resume.

qomrade itself provides three separate evidence surfaces:

- **Session Handoff** carries the observed conversation in order, without an invented summary or new continuation prompt. In 0.18.40, export does not scroll the page; recording follows materialized turns and ordinary user scrolling. Visible file names and image labels can travel as context, not as the contents of those files.
- **Developer Handoff** carries the controller's diagnostic situation, incidents, timeline and supporting evidence for someone repairing qomrade. It is an explicit clipboard export, not an automatic message to the model.
- **Flight Recorder** provides a compact operational first look.

This separation keeps a project transcript from becoming a bundle of controller instructions, and keeps diagnostics from masquerading as the work itself. The [handoff contract](../Maintained%20Tools/qomrade.user.js#L360-L372) explains the boundaries. Moving to another conversation remains an operator decision; qomrade does not create one automatically.

## The delivered tool contains its own workshop

The same `qomrade.user.js` is both the installed browser userscript and a Bash-entry development artifact. The browser runs the JavaScript controller. The Bash entrance opens an embedded Python workbench with current tools, tests, browser fixtures and the project's living documents. A recipient can inspect the complete delivered object rather than first having to reconstruct which distant checkout produced it.

The [workbench entrance](../Maintained%20Tools/qomrade.user.js#L25-L175) exposes source mapping, exact splitting and reassembly, a read-only accepted copy beside an editable candidate, diagnostics, tests and release packaging. Its purpose is not merely convenient unpacking. The candidate workflow distinguishes what was received from what is being proposed, while the release tooling checks that the packaged userscript is the same source that was checked. A complete successor, rather than a patch alone, is the intended handoff.

The [living office and heritage](../Maintained%20Tools/qomrade.user.js#L442-L460) retain the current design, lessons, unresolved questions, decisions and retired machinery. In this version, earlier self-prompting developer loops, fleet coordination, automatic diagnostic uploads and recursively embedded releases have been removed from the browser runtime. Current development tools and bounded lineage remain; exact retired releases belong in a separate developer kit. The package budget is 1 MiB and 12,000 lines, enforced by the carried tooling.

That is an important form of continuity: a successor can shed machinery without losing the reasons for the change. An inheritable workshop need not become an ever-growing museum inside every installed copy.

## Before starting

qomrade runs through Tampermonkey on the matched ChatGPT domains, excluding Codex paths. Review the original header's grants and the runtime contract before installation. Each tab is independent. Stop revokes that tab's automation; it does not click ChatGPT's Stop control. Background operation is supported, but cannot make a browser-suspended tab execute.

Optional generated-file collection activates explicitly named native download controls in completed replies, using the configured suffix list, `.zip` by default. It does not follow arbitrary prose links, and requesting a download is distinct from confirming that it was saved. Website changes can require adapter maintenance; operator-defined project permissions and result review remain part of using the tool.

The original header credits **h0p3 and current/future qomrade officers** and carries an **MIT** notice. Original bytes and carried notices are preserved. [Source receipt](../updates/2026-10-20.json) · [Editorial inspection record](review/qomrade-2026-10-20.md).

[Maintained Tools](../Maintained%20Tools/README.md) · [Catalog](../CATALOG.md) · [W4R3Z](../README.md)
