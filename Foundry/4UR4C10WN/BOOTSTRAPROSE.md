# BOOTSTRAPROSE — rev0294: First Letter readiness and evidence v1

This is the active construction handoff for `4UR4C10WN-rev0294`. Read it before
changing code, tests, documentation, evidence, or package structure. Historical
revision notes are provenance; the maintained present-tense product documents
are named below.

## Read this first

The object is a portable encrypted private post office, not merely a mail client
and not merely an I2P wrapper.

It can carry:

```text
native runtime
exact source and build graph
tests and qualification fixtures
maintained documentation
cryptographic Office state
mail and recovery evidence
an embedded i2pd core
```

The product sentence is:

> **4UR4C10WN is a portable encrypted private post office that can carry its
> runtime, source, tests, documentation, cryptographic office state, and an
> embedded I2P router; it accepts explicit human authority, supports
> recipient-absent delivery, survives interrupted local work, and reports only
> what retained evidence proves.**

The governing implementation rule is:

> **Never turn uncertainty into an automatic retry, a false success, or a
> broader permission.**

The ordinary product should feel simple. The evidence underneath may be deep.

```text
Simple surface
Forensic depth underneath
```

## Active maintained documents

Start here:

```text
docs/CURRENT-PRODUCT.md
docs/CURRENT-ARCHITECTURE.md
docs/CURRENT-CONSTRUCTION-PLAN.md
docs/CURRENT-THREAT-MODEL.md
docs/DURABLE-WRITER-INVENTORY.md
docs/HUMAN-QUICKSTART.md
```

Rev0294-specific design and evidence:

```text
docs/REV0294-FIRST-LETTER-READINESS-V1.md
docs/REV0294-EVIDENCE.md
docs/REV0294-HUMAN-USE-AUDIT.md
```

The rev0292 operator diagnosis/cleanup design, rev0289 foreground-history design,
and rev0290 terminal-lifetime design remain retained provenance. The current
documents describe the shared path-free Task / Recovery integration.

Machine-checked writer contract:

```text
tools/durable_writer_inventory.py
tools/durable_writer_contracts.json
```

Historical revision documents remain useful for provenance, but do not infer
current product behavior from one old release note alone.

## Package contract

The delivered ZIP must be named:

```text
4UR4C10WN-rev0294.zip
```

It must contain exactly two entries, in this order:

```text
4UR4C10WN          mode 0755
BOOTSTRAPROSE.md   mode 0644
```

The external BOOTSTRAP must be byte-identical to the embedded project copy. The
executable must verify its complete image and materialize the exact carried
project.


## Exact lineage

The exact verified direct parent is **rev0293**, carrier SHA-256:

```text
f5a9d6e1eee967ddf16f31ce7bf17285f2c0ce95fe04cbfffb4d97d147c8966e
```

Parent ZIP SHA-256:
`0da2e704f7e996249f30e5fd28e33b846cd0bcc879d44a8b1f9d416a279adf0b`.
The earlier conversation claimed a rev0294 release, but the retained outcome says
NOT PROMOTED and no such ZIP was available. Its checkpoint had no implementation
changes. Do not use that claim as code, qualification or lineage. This rev0294 is
constructed directly from the verified rev0293 project. The inherited rev0291 gap
remains recorded in its parent documents and is not silently repaired.

Preserve every rev0293 path and exact preimages for every edited parent file.

# rev0294 — current construction and next priority

F4 now contains one normal focusable **First Letter** row (`L`). Its five rows are
Office, Route, Posthouse, Contact and Letter. It uses existing observations and
reviewed engines. Typed `V` explains evidence definitions; it does not claim a
selected message exists. The overview is path-free; existing intake/move forms
still require their current expert paths/pins. Portable attached setup parity is
not finished. An open Office is not evidence of a verified backup, storage counts
are not a grant for the next package, and local Route readiness is not public reach.

The explicit `first-letter-lab` command runs a separate real synthetic hybrid mail
assay: recipient absent during signed Posthouse custody, storage restart, retrieval,
key rotation and safe historical-key opening, and deliberately requested ACK1 over
loopback. No automatic read receipt or human-read/public-I2P claim is added.

## Running prioritized checklist

- [x] Reconstruct from exact verified rev0293 rather than unsupported handoff claims.
- [x] Implement the focusable five-stage native/attached readiness projection.
- [x] Reuse reviewed directory, intake, move, readiness and network-status handlers.
- [x] Keep paste, cancellation, no-discard and separate authority boundaries.
- [x] Add and run native regressions, actual blank-Office PTY (37 checks under root
      and ordinary UID), and separate FLA1 assay (13 outer / 81 mail / 6 admission / 11 ACK).
- [ ] Complete the ordinary invitation/pin/grant/Route/send journey, including the
      attached portable adapter; current checklist + separate assay is not that proof.
- [ ] Reconcile sender commit/secondary evidence against authoritative Office state;
      never infer an unsent Letter from a missing local evidence card.
- [ ] Known/introduced/scarce-public first contact and expiring thread-bound reply rights.
- [ ] Rich safe production threads/search/attention/attachments; no active HTML or automatic read receipts.
- [ ] Exact-current two-machine/two-network public I2P, path/power-loss/accessibility,
      and pinned static-musl/reproducible release qualification.

Delivery remains conditional on the actual detached receipt: exact runtime build,
new and retained gates, all parent preimages, self-materialization, passive parent
export, two-entry ZIP validation and tests from that delivered ZIP. The complete
current evidence table is outside the object to avoid circular self-hashing.

Reproduction with a freshly built host runtime and complete carrier:

```sh
python3 tools/build_host.py --jobs 4 --optimization 0 --package
make first-letter-assay FIRST_LETTER_BINARY="$PWD/work/releases/host/4UR4C10WN"
make first-letter-terminal-test FIRST_LETTER_BINARY="$PWD/work/releases/host/4UR4C10WN"
./work/releases/host/4UR4C10WN bootstrap-verify BOOTSTRAPROSE.md
```

The terminal target refuses an existing test-work directory. Supply a fresh
`FIRST_LETTER_WORK` and `FIRST_LETTER_RECEIPT` for another run; never delete real mail
to satisfy a fixture. The fixture uses only disposable synthetic credentials.

## Retained campaign and horizon

The following rev0293-and-earlier sections are retained historical details. Their
past pass counts are not new rev0294 results. The current checklist above and
CURRENT-CONSTRUCTION-PLAN.md control next work. Preserve the wider dream field;
do not let another indefinite series of incidental JSON migrations replace the
ordinary mail experience.

# rev0293 — retained path-free History Task / Recovery

## Human consequence

The evidence model is now reachable without typing a private evidence directory
or a staging filename. F3 History contains one focusable **Evidence and cleanup**
row. Pre-sign-in **Recover closed mail** opens the same center when no valid task
is available, and offers a separately reviewed `evidence` / `INSPECT` route when
valid tasks exist.

Ordinary presentation says what was observed and what remains unavailable or
uncertain. It hides private roots, relative names, hashes, inodes, schema tokens,
and raw record contents. An explicit expert toggle may reveal escaped relative
identity and bounded file facts, but still not the absolute root.

Cleanup remains a second action. The selected item is re-diagnosed before review;
a changed or substituted item is refused. The person must read the complete
review and type `REMOVE-STAGING`. Bracketed paste cannot approve it.

## Shared implementation boundary

```text
F3 History / Recover closed mail
        ↓
human_tui.cpp: path-free presentation and exact typed review
        ↓
carry_resident_ui.cpp: native-selected private roots and bounded worker bridge
        ↓
history_evidence.py: HED1 diagnosis, fresh item commitment, HEC1 review/removal
```

The shared adapter admits only the native-reviewed downloaded-history,
history-results, and history-choice-continuation roots. It produces bounded
private transient state. That state grants no durable action authority.

## Authority boundary

The center cannot authenticate a recovery operation, certify mailbox safety,
repair canonical evidence, retry a worker, apply history, publish navigation,
open or reopen an Office, start an owner or router, send mail, or claim custody.
Schema-specific history validators remain authoritative. The rev0292 expert CLI
remains available as a fallback.

# rev0292 — bounded diagnosis and separately reviewed cleanup

## Human consequence

A retained staging name is not enough to say its publisher died. Age is not
liveness proof. A self-digest is not authenticated mail evidence. File absence is
not proof that a cleanup operation succeeded. This slice makes those distinctions
explicit while providing a usable operator route to remove one eligible remnant.

This is **an operator command surface**, not a new focusable cleanup workflow
inside the ordinary terminal. Recovery and History preserve rejected entries
and direct the operator to the same diagnosis command. Bringing that exact model
into a path-free Task/Recovery interface is the next product task.

## Three commands, three effects

```bash
./4UR4C10WN history-evidence-diagnose /absolute/private/evidence
./4UR4C10WN history-evidence-diagnose /absolute/private/evidence --expert
./4UR4C10WN history-staging-review /absolute/private/evidence STAGING_NAME
./4UR4C10WN history-staging-remove /absolute/private/evidence STAGING_NAME \
  --expect-review=EXACT_SHA256_FROM_REVIEW --approve=REMOVE-STAGING
```

The placeholders must be replaced deliberately. Do not pipe discovery into a
removal loop. Review accepts no approval flag and writes no evidence. Removal
requires both the exact review digest and the distinct approval `REMOVE-STAGING`.
It never accepts OPEN, REMEMBER, or another mail approval as cleanup permission.
This command-line review does not claim the terminal UI's read-all/paste ceremony.

The native routes use the existing isolated, parent-supervised history-child
bridge, materializing only the exact verified standalone `history_evidence.py`
worker into private transient storage. Therefore diagnosis and review are
`TEMPORARY_LOCAL_WRITE` commands even though their **target evidence is read-only**.
Removal is `EXPLICIT_PERSISTENT_WRITE`. These declarations are in the compiled
command catalog. There are now 407 discoverable top-level commands; OPUI's
separate 65-verb catalog is unchanged. The native route table size is now deduced
from its entries rather than duplicated as a hard-coded integer.

## HED1: observation without repair

The scanner opens a normalized absolute directory path component by component,
without following symlinks, retains the chain, and rechecks its identities.
The selected root and traversed evidence directories must be owner-owned mode
0700. Inspected files must be owner-owned, single-linked regular files, mode
0600, read through no-follow descriptors with bounded identity-checked readback.

Bounds are depth 4, 4,096 traversed directory entries, 128 findings, 4 MiB per
record, and 32 MiB total record bytes, including inspected cleanup intent/receipt
records. Reaching a limit produces `complete_scan=false`; it does not imply a
complete healthy inventory. This is an observation, not a filesystem snapshot.
Access times may change as a consequence of reading; other nonmutation claims
are checked against names, types, identities, modes, timestamps, sizes and hashes.

Categories distinguish malformed bytes, a wrong self-digest, canonical-name
conflicts, unknown schemas, unsafe entries, structurally consistent records,
managed staging, legacy staging, and incomplete or receipted cleanup.

Known HCC/HHI/HRI/HHT schemas receive framing, self-commitment and applicable
canonical-name checks only. Schema-specific recovery validators remain the
source of authenticated operation truth. HED1 always reports:

```text
cryptographic_authentication = false
mailbox_safety = not-assessed
```

Unknown schema does not mean corruption. Structural consistency does not mean a
valid task. No output claims that a mailbox is safe merely because this scanner
made no changes. Default output hides all names and paths; explicit expert output
uses bounded relative names and identity/digest details. JSON escapes terminal
controls. Record contents and absolute root paths are not rendered.

## HEC1: only managed v2 regular staging files

The corrected shared publisher now names its private regular staging files:

```text
.history-publish-v2-<32 lowercase hexadecimal characters>.tmp
```

It holds a shared advisory lock on the **exact parent directory** from before
staging creation until publication/cleanup is finished. Multiple cooperating
publishers may hold shared locks. Cleanup/review acquires an exclusive nonblocking
lock on that same directory. A live publisher blocks removal even if the file's
timestamp appears old; a cleaner blocks a new publisher before staging creation.

Eligible files must also be mode 0600, owner-owned, single-linked, at most 4 MiB,
and at least 60 seconds old by the observed modification time. Future timestamps
are refused. Cleanup scans at most 128 parent entries. A new cleanup needs one
free slot for its reservation so that death immediately after directory creation
cannot make explicit resume exceed the same bound.

**Legacy `.history-publish-*.tmp` files, BHR spool staging directories, arbitrary
`.tmp` files, canonical records, active writers, unsafe entries, and full registries
are not removed.** Older publishers do not participate in this lock protocol;
renaming their files to v2 is not a supported migration. Do not infer inactivity
from age, filename, missing PID, or lack of an attached mailbox owner.

## Exact review and removal protocol

Review commits to the complete parent path identity chain, parent device/inode,
name, bounded namespace digest, file device/inode/owner/mode/link count/size,
mtime/ctime, complete SHA-256, protocol version and negative authority declarations.
The resulting digest is a stale-state guard, not standing permission.

A separately approved removal holds the exclusive directory lease and performs:

```text
recompute and match exact review
  → reserve .history-cleanup-<review digest>/ privately
  → atomically publish immutable intent.json; synchronize
  → capture the source as private payload using no-replace rename
  → recheck captured identity and all bytes
  → recheck parent, reservation and payload immediately before unlink
  → unlink only that captured payload and synchronize
  → atomically publish and read back exact receipt.json
```

The parent/root and captured-file identities are rechecked after capture. Rename
changes ctime; every other reviewed field remains exact, and the newly observed
ctime is then rechecked too. A replacement discovered after capture is retained
**inside the cleanup reservation**; it may have moved, but is not unlinked. This
is not a promise that every adversarial race leaves the original pathname intact.

Intent and receipt use private staging, complete write/fsync/readback, no-replace
rename and directory synchronization. No direct-final partial JSON is exposed by
those publishers. There is no overwrite, copy, hard-link or delete-all fallback.
Canonical history records and both mailbox copies remain outside cleanup authority.

## Process death, uncertainty, and explicit continuation

| Retained state | Later explicit invocation with exact review and approval |
|---|---|
| No reservation | Fresh review must still match before any mutation |
| Reservation without a valid intent | Refuse, preserve, diagnose; no deletion |
| Valid intent and exact original source | Capture, recheck and remove only that source |
| Valid intent and exact captured payload | Recheck and finish only that payload |
| Source and payload both present | Preserve both; do not choose a winner |
| Exact receipt retained | Return it without rewriting or deleting a later same-name file |
| Intent, but neither source nor payload and no receipt | Report `absence-observed-not-attributed`; manufacture no success receipt |
| Damaged or substituted intent/receipt/payload | Preserve and refuse |

No operation retries itself. The human/operator must invoke a new action.
The unlink and the later receipt are not one transaction. A worker killed between
them may have removed the reviewed payload, but no later observer can truthfully
attribute bare absence from those records alone. Missing success output is not
failure evidence and not permission to delete something else.

## Scope, not a universal filesystem claim

This coordination protects participating processes on the same supported local
Linux kernel/filesystem. `flock` is advisory; `unlinkat` removes a pathname, not
an inode conditionally. Capture, private namespaces and final rechecks do not
create a universal compare-and-unlink primitive. Arbitrary same-UID/root/kernel
namespace mutation, noncooperating legacy publishers, cross-host locking, power
loss, all-filesystem durability, and secure erasure are not qualified.

A cleanup receipt means a local reviewed unlink was observed. It is not a mail
receipt, storage-custody receipt, human acknowledgement, cryptographic operation
proof, backup deletion, or proof of erased storage blocks. Cleanup reservations
and receipts themselves remain; this release is not an unbounded garbage collector.

## Current pre-freeze evidence

The standalone campaign passes 115 checks under uid 0 and uid 1000. Each run
includes 11 actual process SIGKILLs and one two-remover race; counts overlap and
must not be added as independent properties. The native CLI campaign has 15
checks. Retained publication, TLG1, HCC/HHS, TUI, Office and discovery regressions
are recorded in `REV0292-EVIDENCE.md`. Exact native runtime hashes and source
hashes bind the reduced audit lane. Full release/ZIP proof is a separate lane.

An initial native compilation refused the old fixed-size 404-entry route table
after adding three routes. The table now deduces its size from the entries; the
final build has 407 routes, 1,249 discovery checks, 153 all-Clang native runtime
units and 85 Python tools. The failed construction attempt is not counted as a
passing build. Diagnostic cumulative-byte and cleanup-reservation capacity bugs
found during final review were fixed and the 115-check final-source campaign was
rerun under both privilege levels.

# Current product truths inherited from earlier revisions

## Carrier and project identity

The carrier can:

```text
verify its complete image
report /run status
list and read bounded resources
materialize the exact project
verify project namespace, bytes, and modes
compare candidates without executing them
passively export a pinned candidate
```

Do not substitute runtime SHA-256 for complete carrier SHA-256. Do not substitute
an exact-runtime audit carrier for the delivered release carrier.

## Office and identity

An encrypted Office can contain:

```text
master/profile authority
relationship and contact records
I2P route state
encrypted mailbox state
Library objects
drafts
Outbox and Sent evidence
recovery and checkpoint evidence
```

Route authority, storage grants, relationship authority, and mailbox authority
remain separate.

## Recipient-absent delivery

A configured Posthouse can retain opaque encrypted mail while a recipient is
offline. Signed custody means that one named service accepted exact opaque
bytes. It does not prove recipient retrieval, software opening, human reading,
or understanding.

Use exact language:

```text
Prepared
Queued locally
Attempted
Storage custody accepted
Retrieved
Authenticated and opened
Explicitly acknowledged
Read / understood — not automatically knowable
```

## Safe rendering

Production presentation treats hostile text as data. It does not execute active
HTML, fetch remote images, or blindly emit terminal controls, bidi controls,
zero-width formatting, malformed UTF-8, or attachment names.

## Morrow local automation handoff

Morrow's optional local plaintext handoff uses this order:

```text
publish complete deterministic handoff
        ↓
record monotonic local opened facts
        ↓
publish exact local completion
```

A later explicit invocation can finish pending local bookkeeping. No automatic
read receipt, remote acknowledgement, network operation, human-read claim, or
automatic retry is created.

The plaintext-at-rest fact remains explicit. Mode 0600 is not encryption and
removal is not claimed secure erasure.

## OPUI machine contract

One authoritative 65-command table drives:

```text
emitted schema
help/admission classification
delegated reads
independent actions
resident queries
```

The production machine surface includes:

```text
threads
thread THREAD_ID
thread-window ID
close alias
```

Discoverability is not authority.

## Recovery truth model

The current lifecycle can express:

```text
Saved choices
Prepared
Mailbox closed
Recovery boundary saved
Application attempt saved
Applying
Needs verification
Result verified — not remembered
Result ready
Open
Rollback available
```

Retained evidence does not reuse approval. A live lease does not prove byte
progress. Missing navigation does not mean missing result. A result without
completion must be verified rather than applied again.

The decisions remain separate:

```text
SELECT
CLOSE
APPLY CHOICES
VERIFY
INSPECT
REMEMBER
OPEN
REOPEN
```

## BHR1 and BHR3

Current qualified continuity rules include:

- BHR1 immutable plan and local completion publish complete-or-absent;
- initial BHR1/BHR3 spool namespaces publish as whole directories;
- later journals are mutable atomic old-or-new;
- content-addressed objects retain exact digest/size verification;
- either valid BHR3 credential reconstructs its exact complement;
- authenticated stream completion is the strong completion anchor;
- local BHR1 completion is its deterministic derivative;
- stream-only completion is repairable; and
- BHR1-only completion cannot reconstruct authenticated stream evidence.

The general rule is:

> Preserve the stronger surviving evidence. Derive only records it uniquely
> determines. Never reconstruct stronger evidence from a weaker summary.

## Checked writer census

The checked writer contract, deliberately updated and rerun for rev0292, covers:

```text
selected modules:                         15
reviewed writer sites:                   122
production sites:                         85
test/diagnostic sites:                    37
remaining production design/migration:   28
unreviewed sites:                          0
stale contracts:                           0
changed reviewed contexts:                 0
```

Remaining classification:

```text
complete-or-absent migrations: 24
multi-object design:             1
mutable initialization design:   1
streaming publication design:     2
```

Reviewed-sites digest:

```text
d8539a9c53b88cd26770c451310bbcb4d20286ae710603d81f4d5f7df678c3dd
```

This is not a whole-project census of every C++/SQLite, i2pd, third-party, build,
or future-language write.

# Durable publication map

## Qualified complete-or-absent history records

```text
HRI2  result navigation and REMEMBER
HCA2  external receipt-choice completion
HCC1  reviewed CLOSE continuation
HCC2  pre-owner recovery boundary
HCC3  authenticated application attempt
HCD1  saved deferred choices
HCA1  application readiness
HHT1  downloaded-history task
HRI1  first-generation result navigation
HHI1  downloaded-task navigation
HHS3  invitation card
BHR1  immutable plan
BHR1  local completion
BHR3  source credential
BHR3  target credential
BHR3  authenticated stream completion
BHR3  local completion derivative
BHR4  reviewed resident session
BHR4  completed-session receipt
```

The same primitive does not make these records semantically interchangeable.
Each needs its own validator, replay rule, negative claims, and human meaning.

## Whole initial namespaces

```text
BHR1 initial spool directory
BHR3 initial spool directory
```

Later journals retain atomic replacement semantics.

## Personal-mail records

```text
queued-send evidence
Morrow standing private credential
Morrow deterministic plaintext handoff
Morrow opened-completion record
```

## Remaining writer families

Twenty-four immutable sites remain, led by:

```text
BHR2 reviews and results
HCA2 review variants
BHR2/HHA review
BHR3 authenticated session creation
PCH1/PCH2/PCH3/PCH4 plans, reviews, choices, decisions, and results
HCM1 reviewed choices
```

One multi-file HHA action state, one initial mutable HCM state, and two
personal-mail runtime streaming sites still need design.


The changed publisher enclosing-function commitment was reviewed for its shared
parent lease and managed v2 staging family. Counts are unchanged; no remaining
production migration is declared fixed by moving a manifest hash. HEC1's own
writers and tests have the separate current technical/evidence contract.


# Running prioritized construction checklist

## Completed in rev0293

- [x] Verify and materialize exact rev0292.
- [x] Share one HED1/HEC1 adapter between F3 History and pre-sign-in Recovery.
- [x] Keep ordinary evidence presentation path-free.
- [x] Add explicit bounded expert relative identity.
- [x] Re-diagnose the selected item before cleanup review.
- [x] Require full review and typed `REMOVE-STAGING`; pasted approval is inert.
- [x] Preserve all mail, recovery, owner, retry, and network authority boundaries.
- [x] Add a real PTY journey and focused nonmutation/substitution tests.
- [x] Update current product, architecture, threat, quickstart, evidence, and human-use documents.
- [ ] Freeze exact evidence counts, preimages, hashes, passive export, and final ZIP qualification.

## Priority 1 — blank Office to recipient-absent Letter

Use the production Office, embedded Route, Posthouse/storage, and Contact engines
to take one new encrypted Office through one recipient-absent test Letter. Present
local readiness, storage custody, retrieval, software authentication, explicit
acknowledgement, and human reading as separate facts. Keep the journey ordinary,
path-free, and evidence-backed.

## Priority 2 — finish high-value durability and sender reconciliation

The selected census still has 28 production design sites: 24 immutable migrations,
one multi-object HHA action state, one mutable HCM initialization, and two runtime
streaming publishers. Inspect authoritative Outbox/Sent before repairing secondary
sender evidence; never resend merely because the side receipt is absent.
Do not spend the next turn mechanically reducing a site count instead of solving
a demonstrated human or data-safety problem.

## Priority 3 — scoped maintenance, measurement and platform evidence

Design legacy-staging liveness/migration separately; do not relabel old files as
managed v2. Review retention of cleanup intent/receipts and full registry handling.
Measure startup, peak memory, owner downtime, verified bytes and objects, and disk
growth using direct observations, not lease-based guessed progress. Continue path
custody, physical-power-loss, supported-filesystem, terminal, accessibility,
localization, static-musl and reproducible-release work with exact claim boundaries.

## Priority 4 — first contact and excellent everyday mail

Build known / introduced / scarce-public trust tiers and narrow expiring reply
capabilities. Move rich thread/search/attention/snooze/attachment interactions from
the practice surface into the real encrypted Office without active HTML, remote
images, automatic read receipts, historical opened-state falsification or implicit
resend. Keep the postal commons, ferry, conversation-capsule and delegated-device
horizon visible, but do not displace the first useful letter.

## Amazing I2P email experience

The product destination remains one calm journey:

```text
Create or recover Office
        ↓
Route becomes ready
        ↓
Add one Posthouse
        ↓
Import first Contact
        ↓
Write a safe Letter
        ↓
Send while recipient is offline
        ↓
See exact custody/retrieval/open/acknowledgement facts
        ↓
Recover cleanly from interruption
```

The ordinary interface should use seven nouns:

```text
Office
Contact
Route
Posthouse
Letter
Task
Recovery
```

Expert mode may expose exact evidence graphs, digests, file identities,
authority used, mutation performed, uncertainty, and replay safety.

### First-contact model

Keep three visible tiers:

```text
Known Contact
Introduced Contact
Scarce public first contact
```

A letter may carry a narrow, expiring, thread-bound reply capability. It must
not carry executable behavior or silently install durable relationship
authority.

### Production mail UX

Bring useful practice-interface work into the real Office:

```text
rich threads
guarded spam review
bulk actions with review
Needs attention and Snooze
safe constrained Markdown
labels and reviewed rules
privacy-scoped search
large resumable attachments
account separation
attachment conflict handling
```

Keep out:

```text
automatic read receipts
active HTML
remote image fetch
implicit resend
historical opened-state falsification
```

### Longer cool horizon

Product-worthy future directions include:

```text
voluntary encrypted postal commons
narrow powers carried in letters
sneakernet ferry mode
conversation capsules with verifier/reader
delegated personal devices
private archive ingestion
transport-neutral custody
honest deletion and expiry evidence
tiny offline groups after single-owner continuity is mature
```

Do not let these displace onboarding, first contact, public qualification, and
production mail usability.


# Reproduce and qualify from the carried project

## Verify before executing new actions

```bash
./4UR4C10WN verify
./4UR4C10WN /run
./4UR4C10WN bootstrap-verify BOOTSTRAPROSE.md
./4UR4C10WN docs-read docs/BOOTSTRAPROSE.md
./4UR4C10WN project-materialize /private/new-project
./4UR4C10WN project-verify /private/new-project
```

The original parent can passively inspect/export a hash-pinned candidate without
executing it. Whole-carrier, runtime, bundle and Office hashes are distinct.
These commands do not authorize a mailbox owner or network startup.

## Compile exact native inputs

```bash
make check-repository-inputs
PYTHONDONTWRITEBYTECODE=1 python3 tools/build_host.py --jobs 4 --optimization 0
```

This is an unpinned dynamic Linux development build: 153 native runtime units,
all Clang, fatal project warnings, -O0, stripped runtime. Never edit native inputs
while a compiler reads them. Compare active-input and runtime hashes with the
build record before packaging. There is no new native translation unit in rev0293.

## Reproduce diagnosis and cleanup

```bash
make history-evidence-test
make history-evidence-cli-test HISTORY_EVIDENCE_BINARY=/absolute/path/to/4UR4C10WN
PYTHONDONTWRITEBYTECODE=1 python3 tools/durable_writer_inventory.py --output /private/new-inventory.json
make terminal-lifetime-test CXX=clang++ TERMINAL_LIFETIME_WORK=/private/new-terminal-campaign
```

The first two targets use disposable synthetic evidence, never a real Office.
The API fixture performs real spawned publisher/remover deaths and one race.
The command fixture exercises actual native dispatch and its exact extracted
worker. Use an ordinary unprivileged account as well as any privileged build
account. No test is permission to delete user mail or old staging directories.

The focused terminal target compiles production TLG1 into its separate fixture;
the test-only guard-death seam is not a release-runtime object. The larger retained
`make history-recovery-terminal-test` authentic encrypted-mail campaign remains
available; it requires a fresh exact-root native build and private workspace,
and is not claimed as rerun simply because the focused terminal test passes.

## Freeze docs, evidence and preimages; then assemble the full object

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tools/build_host.py --package --jobs 4 --optimization 0
```

A release procedure may invoke the exact built forge/runtime directly after
checking the build record, using the entire frozen project as resource root.
A reduced audit carrier is only a test artifact. It must bind exact runtime and
worker hashes, and does not replace full-carrier or lineage qualification.
Work directories and Python bytecode are not carried.

Retain every rev0292 path and every edited parent preimage under
`history/rev0293-parent-preimages/`. For opaque Python/JSON/Makefile preimages,
append `.md` when required by the resource export contract; preserve exact bytes.
Carry the preimage manifest, technical design, tests and pre-freeze evidence.

The verified rev0292 parent must passively export the hash-pinned final candidate:

```bash
./rev0292-4UR4C10WN carrier-project-materialize ./4UR4C10WN /private/parent-export --expect-sha256=FINAL_CARRIER_SHA256
```

Compare authored, self-materialized, parent-exported and actual ZIP-materialized
trees in names, types, file bytes, file modes and directory modes. The ZIP has
only the executable (0755) and BOOTSTRAP (0644), in that order. Verify CRC and
byte-exact extraction, run full-image verification and /run, verify BOOTSTRAP
identity, and repeat defining tests from the extracted project and executable.
Keep detached post-freeze receipts bound to final hashes. Do not claim packaging
from a report written before the archive was reopened.

# Exact claim boundary

Rev0293 qualifies the shared path-free Task / Recovery presentation, explicit
expert disclosure, separately reviewed single-item managed-staging cleanup, and
the named retained control gates. It does not establish:

```text
rev0291 source or artifact lineage
full cryptographic authentication by HED1 or inference of mailbox safety
legacy staging-file or staging-directory cleanup
bulk deletion, legacy staging cleanup, or canonical repair
atomic unlink-by-inode under arbitrary hostile same-UID namespace mutation
one transaction spanning unlink and cleanup receipt publication
secure erasure, remote deletion, or retirement of every cleanup receipt
physical-power-loss or all-filesystem durability
cross-host/cross-namespace owner or writer exclusion
whole-project durable-writer coverage
restoration after simultaneous launcher-and-terminal-guard death
restoration over a new foreground group or unrecognized terminal mode
non-Linux terminal portability or every interior owner-start kill boundary
exact-current public two-machine/two-network I2P qualification
complete public-stranger/Sybil abuse resistance
sender-commit/secondary-evidence transactionality
continuous synchronization or general multi-writer convergence
accessibility/localization or pinned static-musl/reproducible release qualification
```

Retained parent authentic mail/owner evidence remains provenance, not a claim
that every expensive encrypted-mail campaign was repeated here. Current focused
TLG1, HTR1 ordinary/expert PTY, native command, lifecycle, publication, Office,
and command-discovery gates were rerun. See the revision evidence ledger for
exact lanes and the detached promotion receipt for actual delivered bytes.

Keep the prioritized checklist in user chat and update this handoff each turn.
The next construction should connect the diagnosis/review model to the ordinary
Task/Recovery experience and then advance blank-Office onboarding, rather than
consume another unbounded sequence of releases on incidental schema maintenance.
