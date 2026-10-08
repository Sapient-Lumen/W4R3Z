# Cube deep audit rev0239: sendability over downstream completion

## Bottom line

The riskiest unfinished work is still `FT-0181`: the cube needs a real `SRC2+`
owner-reviewed packet and still has none. The new failure found in this pass was
not lack of doctrine. It was a practical mismatch between the field-facing
micro-packet request and the machine-readable ready request.

Rev0238 made the human ask small. The ready request in
`examples/real-data-requests/ft0181-minimum-real-data-request.json` still asked
for downstream artifacts such as completed workbench, decision-board, and
live-window fields inside `minimum_packet_fields`. That made the request look
ready to lint but less ready to send.

Rev0239 refactors that lane so the first owner contact is genuinely sendable.
The downstream gates stay in force after receipt, but they are no longer treated
as first-email fields.

## What was missing

The missing piece was not another schema family, closure artifact, or broad
registry. The missing piece was phase separation:

- **before receipt:** send one micro-packet request that a real owner can answer;
- **after receipt:** run the owner packet workbench, decision board, change
  ticket, custody review, live-window controls, readout, dispatch, closeout, and
  signoff only if a real packet exists.

The cube had the second phase well covered. It was still leaking second-phase
language into the first-phase ask.

## What changed

- Refactored `examples/real-data-requests/ft0181-minimum-real-data-request.json`
  so the ready request asks for service, owner path, source system, date range,
  cohort aggregate, task and AI action, fallback, incidents, workload, training,
  public claim ceiling, stop condition, redaction assertion, and owner
  attestation.
- Removed downstream completion artifacts from `minimum_packet_fields`.
- Updated `tools/check_real_data_requests.py` so a ready request fails if it
  requires completed downstream gates as first-ask fields.
- Updated `minimum-real-data-request-packet.md`, the first pilot sprint pack,
  the owner import action kit, and the owner field request so they agree on the
  same phase boundary.

## What should change next

The next useful move is still external or near-external:

1. send or adapt the owner field request for one plausible owner;
2. if no owner exists, name the missing owner path rather than adding controls;
3. if an owner rejects the ask as too broad, trim fields and preserve the block;
4. if an owner sends a real minimized packet, then and only then run the
   workbench and downstream gates.

Do not ask the first owner to complete internal archive paperwork before the
first packet exists. A first owner request should be something a service owner
could answer in a short table or memo.

## Audit/refactor finding

The real-data-request plane had become partly post-receipt governance hidden
inside pre-receipt collection language. That is wasteful because it raises the
cost of the only step that can move `FT-0181`: getting a real owner-reviewed
packet.

The corrected invariant is:

> A ready request must be sendable before it is comprehensive.

Comprehensive controls still matter, but only after a packet exists. Before
receipt, the archive should prefer minimization, redaction, owner attestation,
and clear stop conditions over workflow completeness.

## Speculative working diagnosis

The cube tends to make downstream review safer by moving review requirements
earlier. That is usually protective, but it can become harmful when the earlier
step is a human outreach step rather than an internal audit step. In `FT-0181`,
that pattern risked turning a simple owner ask into an archive training exercise.

The durable correction is to mark phase boundaries more aggressively. If a field
belongs to staging, acceptance, public rendering, lifecycle decision, live-window
control, readout, dispatch, closeout, or signoff, it should not appear as a first
owner request field unless the owner naturally owns that fact.

## Closure boundary

Rev0239 does not import real pilot evidence, does not close `FT-0181`, does not
upgrade examples into source evidence, and does not prove learning, safety,
access, workload, compliance, or service effectiveness. It makes the next real
owner ask smaller and adds a targeted guard against the request becoming bloated
again.
