# Architectural change intake

Status: mandatory checklist for significant architectural additions. Updated
2026-09-17.

Use this before merging a change that adds a durable subsystem, crosses a new
trust boundary, changes authority, changes storage/recovery behavior, changes
routes, changes terminal execution, adds a support artifact, or creates a new
operator ceremony.

The purpose is not bureaucracy. The purpose is to keep a hopeful addition from
accidentally weakening IoTox's constitution.

## One-page dossier

Every significant change should have a short dossier before code or alongside
the first PR:

```text
name:
human story:
new capability:
affected layers:
new durable state:
new authority or capability bits:
new local/remote inputs:
new outputs/artifacts:
failure modes:
rollback/freshness story:
support/diagnostics story:
evidence target:
nonclaims:
```

If the dossier cannot say the human story in one paragraph, the change is not
ready to become architecture.

## Layer check

State exactly which layers are touched:

- local CLI or ratox-style filesystem surface;
- same-user control socket;
- Agent business logic;
- stable identity or authority ledger;
- durable command journal;
- sync namespace/policy/store/projection;
- route worker or transport provider;
- Ratox profile/session/process boundary;
- update lifecycle;
- diagnostics/support bundle;
- repository tooling only.

No business-logic change may bypass the transport adapter and call toxcore
directly. No tooling change may become hidden product authority.

## Authority check

Answer these before implementation:

- Does this require a new capability bit, role, or namespace membership edge?
- Can an existing friendship accidentally become authority?
- Can a remote peer choose a local path, executable, argv, route fallback,
  sudo posture, or support content?
- Does a retry widen authority or merely repeat the exact same act?
- How is revocation observed, and what remains as history only?

Default answer: keep friendship, authority, profile binding, sync membership,
and support artifacts separate.

## Storage and freshness check

If the change writes durable state, name:

- every new file family;
- owner/mode/no-follow requirements;
- atomicity and fsync boundary;
- recovery after process death;
- recovery after abrupt storage interruption;
- old-valid rollback behavior;
- corruption behavior;
- whether existing witness/checkpoint lanes cover it.

Never describe a storage mechanism as backup. If backup or restore enters the
story, also state the independent custody requirement.

## Route and privacy check

If the change uses networking, name the route class and fallback policy:

- Tox/native;
- Tox/Tor;
- Tox/I2P;
- local fixture/mock;
- future direct transport, if any.

Route labels are evidence scope. A route success is not an anonymity proof.
Privacy routes must not silently fall back to native.

## Terminal/process check

If the change can execute code, open a PTY, alter profiles, or affect sudo,
state:

- which fixed executable/profile is selected;
- who selected it;
- whether sudo is involved;
- which host policy remains authoritative;
- how stale executable/toolbox paths are detected;
- whether route loss, Agent death, and host reboot have separate stories.

Remote-selected exec, arbitrary forwarding, and automatic sudo remain outside
the current product law.

## Diagnostics/support check

If the change needs support visibility, design the redacted view at the same
time as the feature:

- what closed counters or states are useful;
- what paths, keys, aliases, content, endpoints, terminal bytes, logs, and
  configs must never enter a shareable artifact;
- whether the bundle proves integrity, authorship, health, backup, or none of
  those.

Content-free is not information-free.

## Evidence check

Use the claim maturity vocabulary in `docs/governance/claim-maturity.md`.
For each claim, name the narrowest target:

- idea;
- planned;
- compiled;
- unit-verified;
- adapter-verified;
- binary-verified;
- network-verified;
- route-verified;
- target-verified;
- production.

Every “accepted” sentence should have a paired “still does not mean” sentence.

## Documentation check

Before merging, update the active docs that changed:

- `docs/architecture.md` for layering or durable boundaries;
- `docs/roadmap.md` for priority and nonclaims;
- `docs/open-questions.md` for unresolved follow-up;
- `docs/threat-model-draft.md` for new adversaries/trust boundaries;
- relevant protocol/operation docs;
- `docs/human-stories.md`, `docs/edge-of-hope.md`, or
  `docs/pragmatic-guardrails.md` if the human story changes;
- CLI help/tests if an operator entrance changes.

Do not leave the truth only in an ADR or test name.

When the change touches front-door docs, topic help, sync authority examples,
or the architecture/change-control entrance, update and run the
`iotox.docs-coherence` CTest target. That check is intentionally narrow: it
does not prove architecture correct, but it catches public/internal capability
spelling drift, unsafe RecallRoot examples, and missing intake links.

## Rejection tests

A significant addition should have at least one explicit refusal or hostile
case. Examples:

- wrong principal;
- revoked capability;
- wrong route class;
- stale generation;
- old-valid rollback;
- corrupted durable state;
- unsupported filesystem shape;
- missing host prerequisite;
- attempted path/argv/sudo selection by a peer;
- support export trying to include private detail.

The happy path proves construction. The refusal path proves the boundary.
