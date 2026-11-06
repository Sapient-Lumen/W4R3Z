# Datacube

## A project that carries the means to continue

A project can survive as files and still be difficult to resume. A new contributor needs to find the operative question, understand which source belongs to the supplied program, recover material for inspection, and distinguish a proposed change from an accepted successor.

Datacube brings those jobs into one carried object. Its Linux executable contains a documentary project, its native C++ source, and an interface for inspecting both and constructing a descendant. A readable companion stands beside it so a person or model can learn what the object is before executing it. The aim is a useful handoff: enough of the work and its construction machinery travels together for someone else to understand it and make a reviewable next move.

This guide covers **Datacube MAIN rev1227**, the edition supplied in W4R3Z. Other projects in the collection use Datacube carriers with their own delivery contracts; their filenames, commands and package boundaries may differ.

- [Read the supplied bootstrap prose](../Maintained%20Tools/Datacube/BOOTSTRAPROSE.md).
- [Open the supplied Linux x86-64 executable](../Maintained%20Tools/Datacube/datacube).
- [Return to the maintained tools](../Maintained%20Tools/README.md#datacube).

## What travels together

The delivered pair is exactly:

```text
BOOTSTRAPROSE.md
datacube
```

The lowercase executable name matters. The companion is both readable text and a small shell interface to the native program. Its operational account is generated from the binary's route registry and selected project metadata, rather than maintained as an independent set of instructions.

Inside the binary, the **project tree** and **source tree** have separate identities and reading routes. The project contains the operative account, documentary docket, protocols and retained records. The source contains the C++20 implementation, constructor and reusable implementation components, with its own README and build document. A file named `README.md` in one tree is therefore a different object from the identically named file in the other.

The supplied contract identifies 797 project files and 118 source files. Those counts describe this edition, not a format requirement. The small delivered object uses compressed, indexed storage so readers can request particular members without first unpacking the entire project.

The pair belongs in its own directory. Both members must be regular, non-symlink files with a single hard link and mode `0555` for linked use. Git records executable status but does not preserve that exact read-only mode, so a checkout needs its permissions restored before using the linked interface. Keep this guide, recovered files and working notes outside the pair's directory.

## Find the current work before reading all its history

The [bootstrap prose](../Maintained%20Tools/Datacube/BOOTSTRAPROSE.md#read-and-continue-from-the-actual-object) is the first reading. Once a reader has chosen to execute the supplied program, these commands provide a short route into the work:

```sh
./BOOTSTRAPROSE.md run
./BOOTSTRAPROSE.md bootstrap-contract
./BOOTSTRAPROSE.md project-summary
./BOOTSTRAPROSE.md docs
```

Here, `run` is a read-only continuation view. It does not start an autonomous model session. The contract describes the selected phase, focus, obligations and next priority; `project-summary` reads the operative document; `docs` opens the documentary docket. A recorded obligation or proposed next action remains recorded state until somebody actually performs it.

From that entrance, follow a question into one exact file:

```sh
./BOOTSTRAPROSE.md read .datacube/CONTINUATION-GUIDE.md
./BOOTSTRAPROSE.md source-read README.md
./BOOTSTRAPROSE.md source-read BUILD.txt
```

`project-list`, `project-find` and `source-list` provide further discovery. For a program making repeated reads, `agent-stdio` offers a bounded, reusable read process. The ordinary reader does not need that interface to begin.

There is a documentary wrinkle in this edition. The carried source README and build document open with rev1222 headings. The rev1227 continuation guide also retains a construction selection for rev1226 and a qualification-input passage naming rev1223. Take the current revision, release filename and next priority from the native bootstrap contract and current operative account; do not copy an older selection into a new build. The carried documents remain useful, but their revision-specific recipes need reconciliation before execution.

## What a verified pair tells you

Calling `./datacube bootstrap-contract` directly inspects the binary without checking a companion. Its companion status is `NOT_CHECKED`.

Calling through `BOOTSTRAPROSE.md` enters linked mode. That path checks the sibling files, their bindings and the companion's equality with the complete native-generated projection. Merely changing the companion and updating a checksum written inside it does not satisfy this relationship.

These checks establish which local files belong together. They leave other questions to their own evidence: who supplied the object, whether it is the newest edition, whether its runtime was compiled from the reviewed source, and whether a proposed successor has been independently accepted. The [bootstrap's authority account](../Maintained%20Tools/Datacube/BOOTSTRAPROSE.md#authority-evidence-and-historical-continuity) states those limits explicitly.

This separation is useful during collaboration. A reader can establish an exact source relation without pretending to have performed a build, and inspect a recorded experiment without treating the act of reading it as a new experiment.

## From inspection to a descendant

The native interface makes continuation a sequence of distinct operations.

1. **Recover the materials needed for the change.** `project-materialize` and `source-materialize` recover complete trees into fresh targets. They require an existing absolute operation root, a new target name and a 64-character lowercase hexadecimal nonce. The results are read-only: files use mode `0444`, directories `0555`. Preserve those exact inputs and create a separate writable development copy.
2. **Describe the intended change.** `edit-plan` admits or rechecks an exact plan. This edition supports regular-file replacement, addition, removal and rename; empty-directory edits; and bounded transactions within one tree or across project and source. The plan binds the parent and intended contents rather than relying on a filename alone.
3. **Review the complete candidate inputs.** `source-verify` compares the embedded source with an exact external tree. Candidate operations also require complete reviewed project and source trees, with the selected edits applied and unrelated members unchanged.
4. **Construct a local candidate.** `candidate-build` checks the selected inputs and invokes the selected constructor. It writes a fresh, nonrelease result containing `datacube`, `EDIT-PLAN.json`, `LINEAGE.json` and `BUILD-RECEIPT.json`. It does not produce the final companion or the two-file release ZIP.
5. **Verify, qualify and package the successor.** `candidate-lineage` checks the relation among the observed parent, exact plan and supplied candidate without executing the candidate. Building the final linked pair, testing its changed behavior and packing its two files are further steps. Independent review, acceptance and external publication remain separate decisions.

One small source-level example shows why the plan is more than a list of filenames. In rev1227's carried `include/datacube/edit_transaction.hpp`, transaction admission checks selected members and the complete selected carried tree, projects the resulting member set and closes aggregate bounds before acquiring replacement payloads. For removal or rename, it checks the selected member against the expected old size and digest; a rename also requires an unoccupied destination. The replacement inputs are then retained and rechecked. This is an account of the inspected implementation, not a claim that the transaction has been executed or independently qualified here. The exact carried source can be reached through `source-read include/datacube/edit_transaction.hpp`.

This is an orientation to the workflow, not a copy-and-run construction recipe. The native help and exact selected build inputs determine the arguments. Construction executes software: checking its digest identifies that software but does not establish that its behavior is safe. The constructor's child-process limits are not a general effect sandbox.

The final `pack` route creates a deterministic two-member ZIP without replacing an existing archive. In that route, “publication” means creating a local filesystem artifact. It does not upload a release to GitHub or establish independent custody.

## Three boundaries of portability

**The current project and source are carried.** A reader can inspect and recover them through the native interface. Recovery does not supply every tool needed to compile or test them. The source build document calls for Linux x86-64, a C++20 compiler and linker, static C++ runtime support, libzstd headers and a static library, and ordinary filesystem, process and shell facilities. Exact reproduction also depends on the selected toolchain and dependencies.

**Deep history has a separate address.** Rev1153 is the named historical checkpoint. The current carrier records its exact identity, filename, length and digests, but the checkpoint archive must be acquired separately for deep historical audit or legacy execution. Ordinary current re-entry does not fetch or replay it. An exact address can tell a reader which archive is wanted without proving that a copy remains available. Its historical runtime can also have different environmental requirements from the current static Linux x86-64 executable.

**The surrounding construction project is separate.** The documentary docket explicitly places build receipts, test harnesses and the candidate-owned roadmap in the surrounding science/integration workspace. Its optional Python conductor sequences native operations outside the closed C++ source tree. A reference to that conductor is not evidence that the pair contains it. Likewise, a carried historical qualification record reports its own occasion, not a new test of rev1227.

These distinctions let “self-contained” have a useful scope: the current project and source travel with their inspection interface, while historical recovery, compilation, testing and independent judgment keep their actual requirements visible.

## Read it beside DelayBasin

[DelayBasin](../OG%20510P/DelayBasin/README.md) asks what a public artifact must preserve for a later session to recover a project's direction. Datacube gives a related practical problem an executable form: exact current materials, a readable entrance, and explicit ways to inspect and change them.

The connection is a shared question worth exploring. DelayBasin's preserved ZIP research packages and this binary carrier remain different historical objects. Reading them together does not establish one implementation lineage or show that packaging alone solves faithful continuation.

## Edition and sources

This introduction describes the supplied **MAIN rev1227** pair. Its executable is 3,937,037 bytes with SHA-256:

```text
9489d1350172dc8091a944f8c8f1bfb0b9e29d071c12d6b1db7b3f538ba32d34
```

The account was checked against the [public bootstrap](../Maintained%20Tools/Datacube/BOOTSTRAPROSE.md) and these exact carried documents:

- Project: `.datacube/OPERATIVE.md`, `.datacube/DOCUMENTARY-DOCKET.md`, `.datacube/CONTINUATION-GUIDE.md` and `.datacube/DELIVERY-CONTRACT.md`.
- Source: `README.md` and `BUILD.txt`.

Project documents are available through `read PATH`; source documents through `source-read PATH`. Static inspection verified the supplied members and selected document hashes. This editorial review did not execute the binary, compile its source or independently reproduce its recorded tests.

[Maintained tools](../Maintained%20Tools/README.md) · [Catalog](../CATALOG.md) · [W4R3Z](../README.md)
