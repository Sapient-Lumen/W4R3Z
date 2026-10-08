# Architecture — rev0154

## Architectural thesis

Lacuna is an epistemic custody kernel, not an LLM wrapper, storyteller, or autonomous campaign runner. It preserves typed claims, plural candidate worlds, commitments, consequences, evidence-factor custody, fair-play receipts, and access-scoped projections. Revision 0154 adds the missing **model entrance layer**: a fresh chat model, workspace agent, or bounded subagent coordinator can determine what kind of request it received, inspect whether a cube is ready, obtain exact commands and contracts, and enter the existing source-bound turn protocol without relying on author-specific ritual.

The revised system has two distinct control planes:

```text
operator / player intent
        ↓
portable entrance + capability profile
        ↓
verified readiness + exact host loop
        ↓
source-bound turn packet
        ↓
proposal generation / optional bounded delegation
        ↓
atomic commit or structured refusal
        ↓
accepted top-level narration
```

and:

```text
immutable events
        ↓ deterministic replay
semantic projections
        ↓ access policy
human / host / model views
        ↓ typed reviewed proposal
atomic validation + append or refusal
```

The first plane makes the second one discoverable. It does not weaken, duplicate, or replace kernel authority.

## System boundary

```text
player / human operator / external LLM / game engine
                         │
                         │ "Will you DM?" / inspect / develop
                         ▼
             ┌──────────────────────────────┐
             │ model entrance              │
             │ intent router               │
             │ chat/workspace/orchestrated │
             │ readiness + exact commands  │
             └──────────────┬───────────────┘
                            │
                            ▼
             ┌──────────────────────────────┐
             │ governed entrances          │
             │ campaigns · CLI · Python    │
             │ turn packets · JSON schemas │
             └──────────────┬───────────────┘
                            │
                            ▼
             ┌──────────────────────────────┐
             │ authority + validation      │
             │ write grant · exact head    │
             │ visibility · invariants     │
             │ strict source bindings      │
             └──────────────┬───────────────┘
                            │ append or refuse
                            ▼
             ┌──────────────────────────────┐
             │ immutable custody           │
             │ events · changesets · hashes│
             │ schema migrations           │
             └──────────────┬───────────────┘
                            │ deterministic replay
                            ▼
             ┌──────────────────────────────┐
             │ semantic projections        │
             │ claims · worlds · factors   │
             │ commitments · consequences  │
             │ seals · questions           │
             └──────────────┬───────────────┘
                            │
                   ┌────────┴────────┐
                   ▼                 ▼
           audience context    planner context
           disclosure-safe     hidden-state capable
```

The host owns model invocation, transcript body retention, provider selection, tool exposure, subagent creation, secret-file custody, and presentation policy. Lacuna owns deterministic projection, source-bound authority, validation, atomic mutation, refusal, and replay.

## Entrance layer

### Portable model brief

`./lacuna model brief <reference>` emits a `lacuna.model-brief.v1` document in Markdown or JSON. The command is read-only. It can resolve:

- a bare cube;
- a campaign cube with local campaign metadata; or
- a campaign library with a selected campaign.

The brief contains:

- exact cube and campaign resolution;
- current head and compact status;
- deterministic verification readiness;
- active audience and narrator/actor checks;
- an intent router for play, development, and inspection;
- first-response rules;
- a capability profile contract;
- an exact six-step operator loop;
- recovery behavior;
- delegation roles when enabled; and
- explicit boundaries and nonclaims.

Readiness is deliberately narrower than capability. A cube can be ready for a governed turn while the current conversation cannot reach a shell. Conversely, a shell-capable agent can reach a cube that fails verification or lacks the requested agents. Both facts are represented separately.

### Capability profiles, not vendor names

The entrance uses three profiles:

| Profile | Model/host capability | Governed one-message start |
|---|---|---|
| `chat` | conversation only; no reliable local command bridge | no |
| `workspace` | can read files and execute the Lacuna CLI | yes, when readiness passes |
| `orchestrated` | workspace capability plus bounded task contexts/subagents | yes, when readiness passes |

A product or subscription name is not a profile. A ChatGPT Pro conversation without a connected local host remains `chat`. A provider-specific coding agent with shell access is `workspace`. `orchestrated` is appropriate only when a parent can supply exact role inputs and retain sole commit authority.

This prevents optimistic instructions from claiming that an uploaded ZIP or a fluent model can mutate a local cube without an actual bridge.

### Intent routing

The entrance treats session-control utterances as control data, not world evidence:

```text
"Will you DM?"          -> choose play workflow
"Audit the cube"        -> choose contributor workflow
"Verify the ledger"     -> choose read-only inspection
```

A DM request does not mean an in-world action succeeded. A repository checkout does not mean every user request is a coding task. Inspection does not grant narration or mutation authority.

### Exact-input custody

The generated packet command requires the host to set `PLAYER_INPUT` to the exact latest player message:

```bash
"${PLAYER_INPUT:?set PLAYER_INPUT to the exact latest player message}"
```

Unset or empty input aborts in the shell before `turn packet` mutates the ledger. Shell quoting preserves spaces, newlines, and metacharacters as data. Lacuna records the UTF-8 SHA-256 digest and source/provenance metadata; the host retains the original transcript bytes externally.

### Exact operator loop

The model brief specifies one portable loop:

1. verify the cube;
2. capture the exact latest player input;
3. open a source-bound director packet into `/tmp/lacuna-turn-packet.json`;
4. produce exactly one proposal into `/tmp/lacuna-turn-proposal.json`;
5. atomically commit into `/tmp/lacuna-turn-receipt.json`; and
6. present only the receipt's top-level `narration` after acceptance.

Opening a turn is a mutation because it records source digest, authority grant, and provenance. Generating a proposal is not. Committing is a mutation. Proposed prose never becomes an accepted event merely because it is fluent.

## Shared turn response contract

Revision 0154 centralizes the model-facing response contract in `build_turn_response_contract()`. The turn packet and entrance documentation now derive from one semantic template rather than parallel examples.

The default proposal is a complete, valid narration-only object:

```json
{
  "narration": "Write only what the audience experiences now.",
  "revealed_assertion_ids": [],
  "operations": []
}
```

All request-bound identity fields are prefilled by the actual packet. A model can safely replace only the narration and commit no semantic operations. It adds typed operations only when something deserves durable custody.

This replaces a hazardous demonstration template that included fake `replace.me` claim and assertion operations. Examples consumed by models are executable interface surface, not harmless prose; therefore placeholders that pass schema validation must not appear in the default object.

## Multi-agent information-flow architecture

### Why roles are asymmetric

The orchestrated profile is not a majority vote. It uses different contexts to reduce leakage, authority confusion, and self-verification:

```text
fresh packet
    │
    ├── planner: audience + privileged planner context
    │      returns beats, operation candidates, risks
    │
    ├── narrator: audience-only context + scrubbed observable plan
    │      returns prose and observable facts
    │
    ├── proposal builder: fresh packet + approved artifacts
    │      returns exact turn-proposal JSON
    │
    └── verifier: fresh packet + candidate proposal
           returns PASS or path-specific REFUSE

parent alone writes proposal file, commits, and presents receipt
```

The parent must not pass hidden rationales to the narrator for convenience. The omission is the mechanism.

### Least-context roles

- **Planner:** may inspect plural hidden hypotheses and recommend observable beats or typed operations; cannot commit.
- **Narrator:** receives no planner context, world identifiers/weights, hidden motives, or unrevealed seal openings; returns audience prose only.
- **Proposal builder:** preserves packet identity and serializes approved narration/operations exactly; cannot widen the grant or repair stale bindings by hand.
- **Verifier:** checks identity fields, operation authority, provenance/disclosure rules, and placeholder contamination; diagnoses but does not rewrite.
- **Parent/coordinator:** is the only role allowed to invoke packet/commit commands or present accepted narration.

### Provider adapters

Provider-native files make the portable roles discoverable:

- `AGENTS.md` plus `.codex/config.toml` and `.codex/agents/*.toml`;
- `CLAUDE.md` plus `.claude/agents/*.md`;
- `GEMINI.md` plus `.gemini/agents/*.md`;
- `integrations/chatgpt/` for Project/custom-GPT instructions and human-bridge starters.

These are adapters, not authority. They may drift as vendors change syntax. The packet grant and commit validator remain authoritative.

Claude Code and Gemini CLI role definitions use empty tool allowlists for bounded workers. Codex role definitions use read-only sandboxes, but a read-only worker may still inspect readable workspace files. Therefore Codex prompt separation is not a hard confidentiality boundary. Unrevealed fair-play openings and other secrets must remain outside any readable workspace supplied to such agents.

## Chat-only and bridged operation

A conversation-only model can immediately run an enjoyable scene, but it must label that scene once as chat-only and must not claim durable cube mutation. Governed operation requires one of:

- a human who copies the current brief/packet to the model and returns the exact proposal/receipt;
- a connected tool/action that runs the Lacuna CLI; or
- a workspace agent that can execute the commands itself.

Once a fresh packet is supplied, the model stops improvising authority and follows the packet. A failed commit means the proposed narration is not presented as having occurred.

## Existing epistemic kernel retained

Revision 0154 does not change the event schema or database schema. Database schema remains 8; event schema remains 1. The new `model-brief.v1` is an exchange schema and the entrance module is read-only until it directs the host to existing turn commands.

All prior doctrines remain:

- claims are content, not truth;
- unknown is first-class;
- candidate worlds are partial plural hypotheses;
- selected/high-weight is not canon;
- assignment revision is successor lineage, not overwrite;
- commitments govern mutation rather than confidence;
- consequences preserve authored dependence and repair debt;
- fair-play seals bind exact openings under limited assumptions;
- particle weights are planner attention, not calibrated probability;
- factor reconciliation repairs derived attention without rewriting history;
- audience and planner projections remain separate;
- narration is presentation; accepted typed operations mutate state.

## Trust boundaries

### Enforced by Lacuna

- strict exchange schema and unknown-field refusal;
- exact request/source/head/digest bindings;
- packet write grants and operation allowlists;
- audience/world scope limits;
- provenance and declared-disclosure rules;
- no-clobber, commitment, consequence, seal, and factor invariants;
- atomic append or refusal;
- deterministic replay and verification.

### Behavioral only

- provider instruction files;
- a parent promise not to leak hidden context;
- a subagent promise not to use available read tools;
- a model promise to emit JSON without surrounding prose;
- a host promise to retain exact transcript bytes;
- a model's literary quality or semantic judgment.

### Deliberately external

- LLM invocation and model/version selection;
- provider authentication, billing, and network transport;
- transcript body storage;
- secret-file isolation beyond the host filesystem policy;
- automatic world proposal, rollout, resampling, pruning, and scoring;
- prose generation and semantic fact extraction;
- digital signatures, trusted timestamps, public transparency logs, and hostile-host fork detection.

## Failure and recovery

- **Verification fails:** do not open a governed turn; inspect `./lacuna verify` output.
- **Audience or actor missing:** register the intended active agents before play.
- **No bridge:** remain explicitly chat-only or use the human paste bridge.
- **Stale head:** discard the proposal, open a fresh packet, regenerate.
- **Structured refusal:** repair against the same fresh packet only when the head remained unchanged; never patch source-bound fields manually.
- **No durable fact:** commit narration-only.
- **Model wraps JSON in prose:** request one exact object rather than heuristically extracting authority-bearing JSON.
- **Commit fails:** do not present proposed narration as accepted history.
- **Provider subagent unavailable:** degrade to the `workspace` profile, not to ungoverned mutation.

## Architectural nonclaims

The entrance does not prove that a model will follow instructions, that more agents improve fiction, that vendor sandboxes isolate secrets, or that a one-message DM request can mutate a local cube from every chat product. It does make the required path explicit, machine-readable, testable, and provider-portable while preserving the kernel's existing refusal boundary.
