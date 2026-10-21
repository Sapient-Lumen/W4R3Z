# VHK / VisualHotKey

## Make desktop automation feel like part of the desktop

VHK pursues a practical ambition: describe or demonstrate a task, turn it into a short script, run it, watch what happens, and refine it. A hotkey, window activation or sequence of input should feel like an extension of the operator's work, not a procession of unrelated utilities. That ambition involves language, responsiveness and the meaning of an action, not just the ability to emit keystrokes.

The supplied editions contain two substantially different approaches. The earlier source snapshots develop an AHK-shaped Python automation system around an i3/X11 recorder, editable macros and a session-bound resident service. The latest **rev0575** reconstructs a foundation intended to sit beneath **official AutoHotkey v2**, with a Wine patch series and native C++20/C11 services. It is not simply the old system placed inside a binary.

The [rev0575 bootstrap](versions/rev0575/files/BOOTSTRAPROSE.md) introduces that reconstruction. Its [executable Datacube](versions/rev0575/files/vhk) carries the runtime, project, rebuild source, experiments and development account together. The useful question is what this new foundation makes possible, and which parts of the intended desktop experience remain to be joined.

## The earlier recorder makes a demonstration editable

In rev0511, the [lexical X11 recorder](versions/rev0511/files/docs/RECORDER_X11.md) observes input and produces editable YAML steps. Cleanup can merge delay fragments, reduce redundant pointer movement, recover common key patterns and compress supported text sequences. The useful loop is to demonstrate a repeated task, inspect the generated macro, improve its targeting and waits, then replay and refine it.

The [authoring account](versions/rev0511/files/docs/LLM_AUTHORING_LOOP.md) connects that source to recording evidence, review and resident dispatch. Its many status surfaces try to prevent stale session or macro evidence from standing in for the desktop now. That work serves a recognizable activity, even where the later reconstruction rejects its architectural weight. It is an earlier product path, not a recorder already delivered by rev0575.

## Keep the language; rebuild the platform beneath it

The newer design wants ordinary AHK operations to remain the user's vocabulary. It does not propose another parallel language for Linux windows. The hard problem is translating between AHK's Win32 assumptions and Linux's input and window systems: a window handle, synthetic key, focus change and wait all need meanings that survive the crossing.

The carried `docs/NEW_VHK_CORE_PROBLEM.md` makes this product choice explicit. The runner's `plan`, `validate` and `run` routes prepare and launch the official interpreter through Wine rather than parse an AHK imitation. File-backed scripts use explicit path mapping and separate process arguments. Stdin scripts go to AHK's own stdin mode. A future authoring interface can therefore feed an edited script into the same language rather than inventing a second representation at execution time.

The supplied reference pins are AutoHotkey v2.0.26 and Wine 11.16. These identify this historical construction, not a recommendation to treat those versions as current. The runner, native services and patch subjects are constructed; the complete patched-Wine/official-AHK desktop path is not yet established by the carried evidence.

## A batch is more than a row of key presses

An AHK `SendInput` call supplies an ordered array. Splitting it into a new process or independent RPC for every event would introduce different ordering, latency and failure boundaries. VHK instead carries a complete bounded frame across a persistent Unix connection and admits it as one resident sequencer job after the whole frame has arrived.

This matters for an ordinary sequence such as modifier-down, key, modifier-up. Partial arrival must not masquerade as a complete request; an uncertain acknowledgement must not automatically cause the sequence to be sent twice. The transport distinguishes rejection before admission from an attempted effect whose result is uncertain. “One batch” is an admission and sequencing boundary, not a promise that arbitrary desktop effects can be rolled back.

The carried `docs/EXPERIMENT_001_SENDINPUT_BATCH_SEAM.md` describes this seam and its evolution; `src/native/vhk_inputd.cpp` implements the resident side. The latest architecture retains batch-oriented input, a persistent uinput device and a common physical/synthetic state authority as the intended foundation. Physical interception, modifier reconciliation and the complete live round trip remain distinct integration questions.

## Synthetic input must not lose its identity

An injected key passes through several representations before Wine sees it again. A timestamp or similar-looking key code is not enough to establish which source event it was. The provenance mechanism relates device generation, event lane, sequence, type, code and value, with a generation- and topology-scoped mapping between Linux codes and X keycodes.

The subtle case is autorepeat. An X-server repeat may occur without a new evdev repeat record. Consuming the next ledger entry anyway could steal the real key release. The rev0574/0575 model therefore separates observation from removal: inspect a candidate without consuming it, then consume only its exact matching sequence. A server-generated repeat can inherit active key-down lineage without moving the cursor.

That is a substantive semantic choice, not bookkeeping for its own sake. It aims to keep synthetic input classified as synthetic and to prevent one event from borrowing another's metadata. The carried `docs/PROVENANCE_CURSOR_TRANSACTION_rev0574.md` and `src/native/vhk_xi2_provenance.c` explain the distinction. Routing among multiple simultaneous Wine processes is still an open boundary, not settled by the ledger alone.

## A window is a lifetime, not just a number

The native XCB/EWMH service maintains window state and event-driven waits. Its identity combines a service epoch, X window ID and window lifetime. A title or geometry change need not destroy the identity; destruction and later reuse of the same numeric XID must not silently redirect a retained handle to a different window.

The pseudo-handle work is meant to let AHK address native Linux windows through its familiar window operations. The carried `docs/EXPERIMENT_005_STABLE_NATIVE_WINDOW_IDENTITY.md` distinguishes the isolated X11 identity fixture from full Wine integration. The value is concrete: “activate the window I found” should not become “activate whatever now owns this number.”

Rev0575 also repairs a cancellation race in a native wait. Shutting down a blocked connection wakes it without concurrently closing a descriptor that another thread might reuse. But even if an old response wins the race and reports success, the shutdown connection is no longer healthy. The worker must retire that wait stream before accepting its replacement generation. The source in `src/native/vhk_ahk_window_fastpath.cpp` and the carried experiment 024 expose the failure and correction, rather than treating a successful old return as proof of future usability.

## A portable foundation, not an endlessly growing archive

Rev0575 carries 319 project files and 120 rebuild-source files inside the executable, alongside the runtime. The separate bootstrap is its readable entrance. Project and source have distinct read and materialization routes, so the object can support continued construction instead of depending on the survival of one working directory.

The carried custody record says the reconstruction deliberately did not inherit the old 1,098-file implementation. It retains predecessor identities, selected principles and a critical account of what went wrong. Its postmortem argues that too much machinery accumulated around an unsettled product foundation. That is the project's judgment and design decision, not proof that every earlier mechanism was worthless or that the new approach has already succeeded.

The older supplied editions remain preserved below. Their recorder and review loop can be studied on their own merits; they should not be described as already integrated into the newer native foundation. This is a useful example of continuity through selective reconstruction rather than compulsory accumulation.

Rev0575's immediate construction also separates obtaining upstream bytes from admitting an exact source subject. Its local Wine-archive route checks a compiled digest, stages and inspects the tree, records origin and publishes without replacing an existing destination. The final `renameat2(RENAME_NOREPLACE)` operation, not an earlier absence check, decides whether a competing destination blocks publication. This build-side mechanism remains outside the input hot path.

## Read the two approaches without flattening them

- **For the newer product and its present boundary:** read the [bootstrap](versions/rev0575/files/BOOTSTRAPROSE.md), then the carried project `README.md`, `docs/NEW_VHK_CORE_PROBLEM.md` and `docs/ARCHITECTURE_rev0575.md`.
- **For precise mechanisms:** follow the carried input-batch experiment, provenance cursor account, stable-window identity experiment and cancelled-wait experiment named above, alongside their native source.
- **For the earlier authoring loop:** begin with the [rev0511 source introduction](versions/rev0511/files/README.md) and its recorder/authoring documents. That edition centers recording, cleanup, replay, inspection and a warm i3/X11 service.
- **For the change of judgment:** compare the [rev0412 stance](versions/rev0412/files/VHK-rev0412-2026.03.22.03.18-proofwriter-signoffhelper-ledgerflow-currentacceptance/README.md), rev0511 and the newer cube's `docs/OLD_VHK_POSTMORTEM.md` and `records/OLD_VHK_CUSTODY.md`.

The carried tests and experiments distinguish component behavior from the missing full desktop integration. The new foundation does not yet deliver universal AHK parity, a complete recorder/studio, or a Wayland backend. That boundary leaves a substantial object to examine: a chosen language, real native mechanisms, specific failure corrections and an inspectable path toward a coherent desktop tool.

Read beside [GlassTTY](../GlassTTY/README.md) for bringing browser conversation into shell workflows, and [Sandcodex](../../guides/Sandcodex.md) for a separately maintained project environment. These are different routes to useful interaction, not one interchangeable automation stack.

## Version shelf and preservation

### Supplied snapshots

The reading route above is selective. This shelf retains every supplied snapshot and its original identity.

- [rev0016](versions/rev0016/README.md): 132 preserved members; `vhk_repo_rev0016.tar.gz`.
- [rev0108](versions/rev0108/README.md): 250 preserved members; `VHK-rev0108-2026.03.05.05.01-oscd-oscudp-controllerglue-pegasus.zip`.
- [rev0205](versions/rev0205/README.md): 466 preserved members; `VHK-rev0205-2026.03.08.15.58-systemdunitstates-serviceorchestration-unitbeacon.zip`.
- [rev0313](versions/rev0313/README.md): 652 preserved members; `VHK-rev0313-2026.03.17.23.59-incidentdrift-historysignals-recoverytruth-pineharbor.zip`.
- [rev0412](versions/rev0412/README.md): 829 preserved members; `VHK-rev0412-2026.03.22.03.18-proofwriter-signoffhelper-ledgerflow-currentacceptance.zip`.
- [rev0511](versions/rev0511/README.md): 1,063 preserved members; `VHK-rev0511-2026.03.28.13.29-repairinstanceproof-witnessalignment-x11lane.zip`.
- [rev0575](versions/rev0575/README.md): 2 preserved members; `VHK-rev0575-2026.08.22.19.06-renamenoreplace-waitstreamretirement-raceclosed.zip`.

[Original identities](PROVENANCE.json) · [Back to OG 510P](../README.md)
